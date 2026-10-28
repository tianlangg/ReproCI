import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def now():
    return datetime.now(timezone.utc)


def uid():
    return str(uuid.uuid4())


class Repository(Base):
    __tablename__ = "repositories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    url: Mapped[str] = mapped_column(Text)
    branch: Mapped[str] = mapped_column(String(150))
    image_id: Mapped[str] = mapped_column(Text)
    pytest_args: Mapped[list] = mapped_column(JSON, default=list)
    config_version: Mapped[int] = mapped_column(Integer, default=1)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80))
    payload_hash: Mapped[str] = mapped_column(String(64))
    repository_id: Mapped[str | None] = mapped_column(ForeignKey("repositories.id"))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"))
    ignored_reason: Mapped[str | None] = mapped_column(Text)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    repository_id: Mapped[str] = mapped_column(ForeignKey("repositories.id"))
    commit_sha: Mapped[str] = mapped_column(String(40))
    branch: Mapped[str] = mapped_column(String(150))
    trigger: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    webhook_delivery_id: Mapped[str | None] = mapped_column(String(100))


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"))
    kind: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(20), default="queued")
    owner: Mapped[str | None] = mapped_column(String(100))
    heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (Index("ix_jobs_queue", "state", "created_at"),)


class Attempt(Base):
    __tablename__ = "attempts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))
    parent_attempt_id: Mapped[str | None] = mapped_column(ForeignKey("attempts.id"))
    tested_sha: Mapped[str] = mapped_column(String(40))
    image_id: Mapped[str] = mapped_column(Text)
    command: Mapped[list] = mapped_column(JSON)
    manifest: Mapped[dict] = mapped_column(JSON)
    fingerprint: Mapped[str] = mapped_column(String(64))
    outcome: Mapped[str] = mapped_column(String(20), default="running")
    exit_code: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    artifact_path: Mapped[str] = mapped_column(Text)
    container_id: Mapped[str | None] = mapped_column(String(100))
    error: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index("ix_attempt_history", "tested_sha", "fingerprint"),)


class TestResult(Base):
    __tablename__ = "test_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("attempts.id"))
    node_id: Mapped[str] = mapped_column(Text)
    phases: Mapped[dict] = mapped_column(JSON)
    duration: Mapped[float] = mapped_column()
    failure: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("attempt_id", "node_id"),)


class Investigation(Base):
    __tablename__ = "investigations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))
    source_attempt_id: Mapped[str] = mapped_column(ForeignKey("attempts.id"))
    test_node_id: Mapped[str] = mapped_column(Text)
    good_sha: Mapped[str | None] = mapped_column(String(40))
    bad_sha: Mapped[str | None] = mapped_column(String(40))
    classification: Mapped[str] = mapped_column(String(40), default="running")
    first_bad_sha: Mapped[str | None] = mapped_column(String(40))
    explanation: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)


class JobEvent(Base):
    __tablename__ = "job_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))
    event_type: Mapped[str] = mapped_column(String(40))
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    message: Mapped[str] = mapped_column(Text)
