import asyncio
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import docker
from sqlalchemy import select

from .config import settings
from .db import Session
from .models import Attempt, Investigation, Job, JobEvent, Repository, Run, TestResult, now
from .results import fingerprint, flake_classification
from .runner import execute, git, prepare_source

OWNER = socket.gethostname() + ":" + str(os.getpid())
TERMINAL = {"passed", "failed", "error", "cancelled"}


def event(db, job_id, kind, message):
    db.add(JobEvent(job_id=job_id, event_type=kind, message=message[:1000]))


def recover():
    client = docker.from_env()
    try:
        for container in client.containers.list(all=True, filters={"label": "reproci.job"}):
            container.remove(force=True)
    finally:
        client.close()
    with Session.begin() as db:
        for job in db.scalars(select(Job).where(Job.state == "running")).all():
            job.state, job.ended_at = "error", now()
            event(db, job.id, "recovered", "Scheduler restarted; leftover container stopped")
            for attempt in db.scalars(
                select(Attempt).where(Attempt.job_id == job.id, Attempt.outcome == "running")
            ):
                attempt.outcome, attempt.ended_at, attempt.error = (
                    "error",
                    now(),
                    "Scheduler interrupted",
                )


def claim():
    with Session.begin() as db:
        job = db.scalar(
            select(Job)
            .where(Job.state == "queued")
            .order_by(Job.created_at)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if not job:
            return None
        job.state, job.owner, job.started_at, job.heartbeat = "running", OWNER, now(), now()
        event(db, job.id, "running", "Scheduler claimed job")
        return job.id


def is_cancelled(job_id):
    with Session() as db:
        return db.get(Job, job_id).state == "cancelled"


def heartbeat(job_id):
    with Session.begin() as db:
        job = db.get(Job, job_id)
        if job and job.state == "running":
            job.heartbeat = now()


def run_attempt(job_id, sha, image_id, repo, manifest, parent_id=None):
    root = Path(settings.artifact_root)
    source = root / "sources" / __import__("uuid").uuid4().hex
    attempt = Attempt(
        job_id=job_id,
        parent_attempt_id=parent_id,
        tested_sha=sha,
        image_id=image_id,
        command=[],
        manifest=manifest,
        fingerprint=fingerprint(manifest),
        artifact_path="",
    )
    with Session.begin() as db:
        db.add(attempt)
        db.flush()
        attempt.artifact_path = str(root / "attempts" / attempt.id)
        attempt_id = attempt.id
    output = root / "attempts" / attempt_id
    try:
        if is_cancelled(job_id):
            result = {"outcome": "cancelled", "error": "Cancelled before start"}
        else:
            prepare_source(repo.url, repo.branch, sha, source)
            selected = manifest.get("test")
            command = [
                "python",
                "-m",
                "pytest",
                "-p",
                "pytest_plugin",
                "--junitxml=/output/junit.xml",
                *manifest.get("pytest_args", []),
                *([selected] if selected else []),
            ]
            with Session.begin() as db:
                db.get(Attempt, attempt_id).command = command
            result = execute(
                attempt_id,
                job_id,
                source,
                output,
                image_id,
                command,
                manifest["timeout"],
                environment=manifest.get("environment"),
                limits=manifest.get("limits"),
                cancelled=lambda: is_cancelled(job_id),
            )
    except docker.errors.ImageNotFound:
        result = {
            "outcome": "error",
            "error": "Unavailable environment: retained image ID is missing",
        }
    except Exception as exc:
        result = {"outcome": "error", "error": f"{type(exc).__name__}: {exc}"[:2000]}
    finally:
        shutil.rmtree(source, ignore_errors=True)
    with Session.begin() as db:
        row = db.get(Attempt, attempt_id)
        row.outcome, row.ended_at = result["outcome"], now()
        row.exit_code = result.get("exit_code")
        row.container_id = result.get("container_id")
        row.error = result.get("error")
        for item in result.get("tests", []):
            db.add(
                TestResult(
                    attempt_id=attempt_id,
                    node_id=item["node_id"],
                    phases=item["phases"],
                    duration=item["duration"],
                    failure=item.get("failure"),
                )
            )
        event(db, job_id, "attempt", f"{attempt_id}: {row.outcome} at {sha[:12]}")
    return attempt_id, result["outcome"]


def source_context(job):
    with Session() as db:
        run = db.get(Run, job.run_id)
        repo = db.get(Repository, run.repository_id)
        params = job.params
        source_id = params.get("source_attempt_id") or params.get("retry_of_attempt_id")
        source = db.get(Attempt, source_id) if source_id else None
        image = source.image_id if source else repo.image_id
        manifest = (
            dict(source.manifest)
            if source
            else {
                "pytest_args": repo.pytest_args,
                "timeout": settings.attempt_timeout,
                "limits": {"cpu": 1, "memory_mb": 512, "pids": 128},
                "environment": {
                    "PYTHONPATH": "/src:/output",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "REPROCI_RESULT_FILE": "/output/tests.json",
                    "TMPDIR": "/tmp",
                },
            }
        )
        if source and "test" in params:
            manifest["test"] = params["test"]
        sha = source.tested_sha if source else run.commit_sha
        return run, repo, source, image, manifest, sha


def repeat(job_id, repo, source, image, manifest, sha, n):
    attempts = [
        run_attempt(job_id, sha, image, repo, manifest, source.id)
        for _ in range(n)
        if not is_cancelled(job_id)
    ]
    return attempts, flake_classification([outcome for _, outcome in attempts])


def bisect_job(job, repo, source, image, manifest):
    good, bad = job.params["good"], job.params["bad"]
    inv = Investigation(
        job_id=job.id,
        source_attempt_id=source.id,
        test_node_id=job.params["test"],
        good_sha=good,
        bad_sha=bad,
    )
    with Session.begin() as db:
        db.add(inv)
        db.flush()
        inv_id = inv.id
    checkout = Path(settings.artifact_root) / "bisect" / inv_id
    evidence = {}
    classification, first_bad, explanation = "inconclusive", None, ""
    started = time.monotonic()
    executions = 0
    try:
        git(
            "clone",
            "--no-checkout",
            "--single-branch",
            "--branch",
            repo.branch,
            "--",
            repo.url,
            str(checkout),
            timeout=120,
        )
        for sha in (good, bad):
            if len(sha) != 40 or git("rev-parse", sha + "^{commit}", cwd=checkout) != sha:
                raise ValueError("Endpoint is not a full SHA in this repository")
            git("merge-base", "--is-ancestor", sha, "origin/" + repo.branch, cwd=checkout)
        git("merge-base", "--is-ancestor", good, bad, cwd=checkout)
        if git("rev-list", "--min-parents=2", good + ".." + bad, cwd=checkout):
            raise ValueError("Merge-containing range is unsupported")
        for sha, expected in ((good, "all_passed"), (bad, "all_failed")):
            attempts, verdict = repeat(job.id, repo, source, image, manifest, sha, 3)
            executions += len(attempts)
            evidence[sha] = {"attempts": attempts, "verdict": verdict}
            if verdict != expected:
                raise ValueError(f"Endpoint {sha[:12]} was {verdict}; expected {expected}")
        output = git("bisect", "start", bad, good, cwd=checkout)
        while "is the first bad commit" not in output:
            if is_cancelled(job.id):
                raise RuntimeError("Cancelled")
            if executions + 3 > 50 or time.monotonic() - started > 900:
                raise RuntimeError("Bisect execution budget exhausted")
            candidate = git("rev-parse", "HEAD", cwd=checkout)
            attempts, verdict = repeat(job.id, repo, source, image, manifest, candidate, 3)
            executions += len(attempts)
            evidence[candidate] = {"attempts": attempts, "verdict": verdict}
            action = {"all_passed": "good", "all_failed": "bad"}.get(verdict, "skip")
            result = subprocess.run(
                ["git", "bisect", action], cwd=checkout, text=True, capture_output=True, timeout=60
            )
            output = result.stdout + result.stderr
            if result.returncode and "first bad commit" not in output:
                raise RuntimeError(
                    "Git could not identify a unique first bad commit: " + output[:500]
                )
        candidate = git("rev-parse", "HEAD", cwd=checkout)
        parent = git("rev-parse", candidate + "^", cwd=checkout)
        for sha, expected in ((parent, "all_passed"), (candidate, "all_failed")):
            attempts, verdict = repeat(job.id, repo, source, image, manifest, sha, 3)
            evidence["confirm:" + sha] = {"attempts": attempts, "verdict": verdict}
            if verdict != expected:
                raise RuntimeError("First bad commit confirmation was inconclusive")
        classification, first_bad = "first_bad_found", candidate
        explanation = (
            "First observed breaking commit under fixed image and linear-history assumptions"
        )
    except Exception as exc:
        explanation = str(exc)
    finally:
        if checkout.exists():
            subprocess.run(
                ["git", "bisect", "reset"], cwd=checkout, capture_output=True, timeout=30
            )
            shutil.rmtree(checkout, ignore_errors=True)
    with Session.begin() as db:
        row = db.get(Investigation, inv_id)
        row.classification, row.first_bad_sha = classification, first_bad
        row.explanation, row.evidence = explanation, evidence
    return "passed" if first_bad else "error"


def process(job_id):
    with Session() as db:
        job = db.get(Job, job_id)
        kind, params, run_id = job.kind, job.params, job.run_id

    class Snapshot:
        pass

    job = Snapshot()
    job.id, job.kind, job.params, job.run_id = job_id, kind, params, run_id
    try:
        run, repo, source, image, manifest, sha = source_context(job)
        if kind == "suite":
            _, state = run_attempt(
                job_id, sha, image, repo, manifest, source.id if source else None
            )
        elif kind == "replay":
            _, state = run_attempt(job_id, sha, image, repo, manifest, source.id)
        elif kind == "flake":
            attempts, verdict = repeat(
                job_id, repo, source, image, manifest, sha, params["repeats"]
            )
            with Session.begin() as db:
                evidence = []
                for attempt_id, outcome in attempts:
                    test = db.scalar(
                        select(TestResult).where(
                            TestResult.attempt_id == attempt_id,
                            TestResult.node_id == params["test"],
                        )
                    )
                    evidence.append(
                        {
                            "attempt_id": attempt_id,
                            "outcome": outcome,
                            "failure": test.failure if test else None,
                        }
                    )
                inv = Investigation(
                    job_id=job_id,
                    source_attempt_id=source.id,
                    test_node_id=params["test"],
                    classification=verdict,
                    explanation=f"{len(attempts)} fixed-input isolated attempts; errors do not establish flakiness",
                    evidence={
                        "counts": {
                            key: sum(item[1] == key for item in attempts)
                            for key in ("passed", "failed", "error", "cancelled")
                        },
                        "attempts": evidence,
                    },
                )
                db.add(inv)
            state = "passed" if verdict != "inconclusive" else "error"
        elif kind == "bisect":
            state = bisect_job(job, repo, source, image, manifest)
        else:
            state = "error"
    except Exception as exc:
        state = "error"
        with Session.begin() as db:
            event(db, job_id, "error", str(exc))
    with Session.begin() as db:
        row = db.get(Job, job_id)
        if row.state != "cancelled":
            row.state = state
        row.ended_at = now()
        event(db, job_id, row.state, "Job finished")


async def supervise(job_id):
    task = asyncio.create_task(asyncio.to_thread(process, job_id))
    while not task.done():
        await asyncio.sleep(2)
        await asyncio.to_thread(heartbeat, job_id)
    await task


async def main():
    await asyncio.to_thread(recover)
    active = set()
    while True:
        active = {task for task in active if not task.done()}
        while len(active) < settings.max_concurrent_jobs:
            job_id = await asyncio.to_thread(claim)
            if not job_id:
                break
            active.add(asyncio.create_task(supervise(job_id)))
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
