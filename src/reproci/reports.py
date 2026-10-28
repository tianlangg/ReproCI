from sqlalchemy import select

from .models import Attempt, Investigation, Job, Repository, Run, TestResult


def make_report(db, run_id):
    run = db.get(Run, run_id)
    repo = db.get(Repository, run.repository_id)
    lines = [
        "# ReproCI evidence report",
        "",
        f"Repository: `{repo.name}`",
        f"Commit: `{run.commit_sha}`",
        f"Branch: `{run.branch}`",
        f"Trigger: `{run.trigger}`",
        f"Run ID: `{run.id}`",
        "",
    ]
    for job in db.scalars(select(Job).where(Job.run_id == run_id).order_by(Job.created_at)):
        lines += [
            f"## {job.kind}: `{job.id}`",
            "",
            f"State: **{job.state}**",
            f"Started: {job.started_at}; ended: {job.ended_at}",
            "",
        ]
        for attempt in db.scalars(
            select(Attempt).where(Attempt.job_id == job.id).order_by(Attempt.started_at)
        ):
            lines += [
                f"### Attempt `{attempt.id}`",
                "",
                f"Source SHA: `{attempt.tested_sha}`",
                f"Image ID: `{attempt.image_id}`",
                f"Outcome: **{attempt.outcome}**",
                f"Parent attempt: `{attempt.parent_attempt_id or 'none'}`",
                f"Command: `{attempt.command}`",
                f"Fingerprint: `{attempt.fingerprint}`",
                f"Artifacts: `{attempt.artifact_path}`",
                f"Error: {attempt.error or 'none'}",
                "",
            ]
            for result in db.scalars(select(TestResult).where(TestResult.attempt_id == attempt.id)):
                lines += [f"- `{result.node_id}`: {result.phases}; {result.duration:.3f}s"]
                if result.failure:
                    lines += ["  - Failure: " + result.failure.splitlines()[-1][:300]]
            lines.append("")
        inv = db.scalar(select(Investigation).where(Investigation.job_id == job.id))
        if inv:
            lines += [
                f"Classification: **{inv.classification}**",
                f"First bad commit: `{inv.first_bad_sha or 'none'}`",
                f"Explanation: {inv.explanation}",
                f"Evidence: `{inv.evidence}`",
                "",
            ]
    lines += [
        "A single-test replay can remove test-order interactions. Flakiness is only observed within recorded repeats."
    ]
    return "\n".join(lines) + "\n"
