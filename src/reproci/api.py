import hashlib
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select, text

from .config import settings
from .db import Session
from .models import (
    Attempt,
    Investigation,
    Job,
    JobEvent,
    Repository,
    Run,
    TestResult,
    WebhookDelivery,
    now,
)
from .reports import make_report
from .webhooks import SHA, valid_signature

app = FastAPI(title="ReproCI", version="0.1.0")


class RepositoryInput(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    url: str
    branch: str = "main"
    image_id: str
    pytest_args: list[str] = Field(default_factory=list)


class RunInput(BaseModel):
    repository: str
    commit: str = Field(pattern=r"^[0-9a-f]{40}$")


class TestInput(BaseModel):
    test: str


class FlakeInput(TestInput):
    repeats: int = Field(default=10, ge=2, le=20)


class BisectInput(TestInput):
    good: str = Field(pattern=r"^[0-9a-f]{40}$")
    bad: str = Field(pattern=r"^[0-9a-f]{40}$")


def repo_by_name(db, name):
    repo = db.scalar(select(Repository).where(Repository.name == name))
    if not repo:
        raise HTTPException(404, "Repository not registered")
    return repo


def get_source_test(db, attempt_id, node_id):
    source = db.get(Attempt, attempt_id)
    if not source:
        raise HTTPException(404, "Attempt not found")
    if not db.scalar(
        select(TestResult).where(TestResult.attempt_id == attempt_id, TestResult.node_id == node_id)
    ):
        raise HTTPException(422, "Exact test node ID was not recorded in this attempt")
    return source


def queue(db, run_id, kind, params):
    job = Job(run_id=run_id, kind=kind, params=params)
    db.add(job)
    db.flush()
    db.add(JobEvent(job_id=job.id, event_type="queued", message="Job queued"))
    return job


@app.get("/health")
def health():
    with Session() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/repositories", status_code=201)
def add_repository(data: RepositoryInput):
    if data.url.startswith("file://") or data.url.startswith("/"):
        pass  # Local demo repositories are explicitly registered by their owner.
    elif not data.url.startswith("https://"):
        raise HTTPException(422, "Use an HTTPS or local file repository URL")
    with Session.begin() as db:
        if db.scalar(select(Repository).where(Repository.name == data.name)):
            raise HTTPException(409, "Repository name already exists")
        repo = Repository(**data.model_dump())
        db.add(repo)
        db.flush()
        return {"id": repo.id, "name": repo.name}


@app.post("/runs", status_code=202)
def add_run(data: RunInput):
    with Session.begin() as db:
        repo = repo_by_name(db, data.repository)
        run = Run(
            repository_id=repo.id, commit_sha=data.commit, branch=repo.branch, trigger="manual"
        )
        db.add(run)
        db.flush()
        job = queue(db, run.id, "suite", {})
        return {"run_id": run.id, "job_id": job.id, "state": job.state}


@app.get("/runs")
def list_runs(limit: int = 20, offset: int = 0):
    with Session() as db:
        rows = db.scalars(
            select(Run)
            .order_by(Run.created_at.desc())
            .limit(min(max(limit, 1), 100))
            .offset(max(offset, 0))
        ).all()
        return [{"id": r.id, "commit": r.commit_sha, "created_at": r.created_at} for r in rows]


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    with Session() as db:
        run = db.get(Run, run_id)
        if not run:
            raise HTTPException(404, "Run not found")
        jobs = db.scalars(select(Job).where(Job.run_id == run_id).order_by(Job.created_at)).all()
        return {
            "id": run.id,
            "commit": run.commit_sha,
            "branch": run.branch,
            "trigger": run.trigger,
            "jobs": [
                {
                    "id": j.id,
                    "kind": j.kind,
                    "state": j.state,
                    "started_at": j.started_at,
                    "ended_at": j.ended_at,
                }
                for j in jobs
            ],
        }


@app.get("/runs/{run_id}/tests")
def get_tests(run_id: str):
    with Session() as db:
        if not db.get(Run, run_id):
            raise HTTPException(404, "Run not found")
        rows = db.execute(
            select(TestResult, Attempt)
            .join(Attempt, TestResult.attempt_id == Attempt.id)
            .join(Job, Attempt.job_id == Job.id)
            .where(Job.run_id == run_id)
        ).all()
        return [
            {
                "attempt_id": a.id,
                "node_id": t.node_id,
                "phases": t.phases,
                "duration": t.duration,
                "failure": t.failure,
            }
            for t, a in rows
        ]


def queue_debug(attempt_id, data, kind):
    with Session.begin() as db:
        source = get_source_test(db, attempt_id, data.test)
        job = queue(
            db,
            db.get(Job, source.job_id).run_id,
            kind,
            {"source_attempt_id": attempt_id, **data.model_dump()},
        )
        return {"job_id": job.id, "state": job.state}


@app.post("/attempts/{attempt_id}/replay", status_code=202)
def replay(attempt_id: str, data: TestInput):
    return queue_debug(attempt_id, data, "replay")


@app.post("/attempts/{attempt_id}/flakes", status_code=202)
def flakes(attempt_id: str, data: FlakeInput):
    return queue_debug(attempt_id, data, "flake")


@app.post("/attempts/{attempt_id}/bisect", status_code=202)
def bisect(attempt_id: str, data: BisectInput):
    return queue_debug(attempt_id, data, "bisect")


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    with Session() as db:
        job = db.get(Job, job_id)
        if not job:
            raise HTTPException(404, "Job not found")
        attempts = db.scalars(
            select(Attempt).where(Attempt.job_id == job_id).order_by(Attempt.started_at)
        ).all()
        inv = db.scalar(select(Investigation).where(Investigation.job_id == job_id))
        events = db.scalars(
            select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.at)
        ).all()
        return {
            "id": job.id,
            "run_id": job.run_id,
            "kind": job.kind,
            "state": job.state,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
            "attempts": [
                {
                    "id": a.id,
                    "parent_attempt_id": a.parent_attempt_id,
                    "sha": a.tested_sha,
                    "image_id": a.image_id,
                    "outcome": a.outcome,
                    "exit_code": a.exit_code,
                    "started_at": a.started_at,
                    "ended_at": a.ended_at,
                    "error": a.error,
                    "artifacts": str(Path(a.artifact_path).name),
                }
                for a in attempts
            ],
            "investigation": None
            if not inv
            else {
                "classification": inv.classification,
                "first_bad_sha": inv.first_bad_sha,
                "explanation": inv.explanation,
                "evidence": inv.evidence,
            },
            "events": [{"type": e.event_type, "at": e.at, "message": e.message} for e in events],
        }


@app.post("/jobs/{job_id}/cancel")
def cancel(job_id: str):
    with Session.begin() as db:
        job = db.get(Job, job_id, with_for_update=True)
        if not job:
            raise HTTPException(404, "Job not found")
        if job.state in ("queued", "running"):
            job.state = "cancelled"
            job.ended_at = now()
            db.add(
                JobEvent(job_id=job.id, event_type="cancelled", message="Cancellation requested")
            )
        return {"id": job.id, "state": job.state}


@app.post("/jobs/{job_id}/retry", status_code=202)
def retry(job_id: str):
    with Session.begin() as db:
        original = db.get(Job, job_id)
        if not original:
            raise HTTPException(404, "Job not found")
        if original.state not in ("failed", "error", "cancelled"):
            raise HTTPException(409, "Only terminal unsuccessful jobs can be retried")
        params = dict(original.params)
        if original.kind == "suite":
            previous = db.scalar(
                select(Attempt).where(Attempt.job_id == job_id).order_by(Attempt.started_at.desc())
            )
            if previous:
                params["retry_of_attempt_id"] = previous.id
        new_job = queue(db, original.run_id, original.kind, params)
        event = JobEvent(
            job_id=new_job.id, event_type="retry", message=f"Retry of job {original.id}"
        )
        db.add(event)
        return {"job_id": new_job.id, "retry_of_job_id": original.id, "state": new_job.state}


@app.get("/runs/{run_id}/report", response_class=PlainTextResponse)
def report(run_id: str):
    with Session() as db:
        if not db.get(Run, run_id):
            raise HTTPException(404, "Run not found")
        return make_report(db, run_id)


@app.post("/webhooks/github")
async def github(request: Request):
    chunks = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > 1024 * 1024:
            raise HTTPException(413, "Payload too large")
        chunks.append(chunk)
    body = b"".join(chunks)
    if not valid_signature(
        body, request.headers.get("X-Hub-Signature-256"), settings.github_secret
    ):
        raise HTTPException(401, "Invalid signature")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")
    if not delivery_id or len(delivery_id) > 100:
        raise HTTPException(422, "Invalid delivery ID")
    event = request.headers.get("X-GitHub-Event", "")
    try:
        payload = json.loads(body)
    except ValueError:
        raise HTTPException(422, "Invalid JSON") from None
    with Session.begin() as db:
        remote = payload.get("repository", {}).get("clone_url", "")
        repo = db.scalar(select(Repository).where(Repository.url == remote))
        reason = None
        if event != "push":
            reason = "unsupported event"
        elif not repo:
            reason = "unregistered repository"
        elif payload.get("deleted"):
            reason = "branch deletion"
        elif payload.get("ref") != "refs/heads/" + repo.branch:
            reason = "other branch"
        elif not SHA.fullmatch(payload.get("after", "")):
            reason = "invalid commit SHA"
        inserted = db.execute(
            pg_insert(WebhookDelivery)
            .values(
                id=delivery_id,
                event_type=event,
                payload_hash=hashlib.sha256(body).hexdigest(),
                repository_id=repo.id if repo else None,
                ignored_reason=reason,
            )
            .on_conflict_do_nothing(index_elements=[WebhookDelivery.id])
            .returning(WebhookDelivery.id)
        ).scalar_one_or_none()
        if not inserted:
            old = db.get(WebhookDelivery, delivery_id)
            return {
                "delivery_id": delivery_id,
                "run_id": old.run_id,
                "ignored_reason": old.ignored_reason,
                "duplicate": True,
            }
        delivery = db.get(WebhookDelivery, delivery_id)
        if not reason:
            run = Run(
                repository_id=repo.id,
                commit_sha=payload["after"],
                branch=repo.branch,
                trigger="webhook",
                webhook_delivery_id=delivery_id,
            )
            db.add(run)
            db.flush()
            delivery.run_id = run.id
            queue(db, run.id, "suite", {})
        return {
            "delivery_id": delivery_id,
            "run_id": delivery.run_id,
            "ignored_reason": reason,
            "duplicate": False,
        }
