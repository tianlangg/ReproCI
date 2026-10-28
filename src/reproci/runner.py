import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import docker

from .config import settings
from .results import classify


def git(*args, cwd=None, timeout=60):
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def prepare_source(url: str, branch: str, sha: str, destination: Path):
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("A full lowercase commit SHA is required")
    if destination.exists():
        shutil.rmtree(destination)
    git(
        "clone",
        "--no-checkout",
        "--filter=blob:none",
        "--single-branch",
        "--branch",
        branch,
        "--",
        url,
        str(destination),
        timeout=120,
    )
    git("fetch", "origin", branch, cwd=destination, timeout=120)
    if git("rev-parse", sha + "^{commit}", cwd=destination) != sha:
        raise ValueError("Commit does not resolve exactly")
    git("merge-base", "--is-ancestor", sha, "origin/" + branch, cwd=destination)
    git("checkout", "--detach", sha, cwd=destination)
    shutil.rmtree(destination / ".git")


def write_bounded(path: Path, data: bytes, maximum: int):
    truncated = len(data) > maximum
    path.write_bytes(data[:maximum] + (b"\n[TRUNCATED]\n" if truncated else b""))
    return truncated


def execute(
    attempt_id: str,
    job_id: str,
    source: Path,
    output: Path,
    image_id: str,
    command: list[str],
    timeout: int,
    max_log_bytes: int | None = None,
    environment: dict[str, str] | None = None,
    limits: dict | None = None,
    cancelled=lambda: False,
):
    """Run one disposable, restricted container. The caller owns source and output."""
    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o777)
    shutil.copyfile(Path(__file__).with_name("pytest_plugin.py"), output / "pytest_plugin.py")
    client = docker.from_env()
    image = client.images.get(image_id)
    actual_id = image.id
    limits = limits or {"cpu": 1, "memory_mb": 512, "pids": 128}
    container = None
    started = time.monotonic()
    try:
        root = Path(settings.artifact_root)
        source_subpath = str(source.relative_to(root))
        output_subpath = str(output.relative_to(root))
        mounts = [
            {
                "Type": "volume",
                "Source": settings.artifact_volume,
                "Target": "/src",
                "ReadOnly": True,
                "VolumeOptions": {"Subpath": source_subpath},
            },
            {
                "Type": "volume",
                "Source": settings.artifact_volume,
                "Target": "/output",
                "ReadOnly": False,
                "VolumeOptions": {"Subpath": output_subpath},
            },
        ]
        container = client.containers.create(
            actual_id,
            command=command,
            working_dir="/src",
            network_disabled=True,
            user="65534:65534",
            read_only=True,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            mem_limit=f"{limits['memory_mb']}m",
            nano_cpus=int(limits["cpu"] * 1_000_000_000),
            pids_limit=limits["pids"],
            tmpfs={"/tmp": "rw,noexec,nosuid,size=128m"},
            mounts=mounts,
            environment=environment
            or {
                "PYTHONPATH": "/src:/output",
                "PYTHONDONTWRITEBYTECODE": "1",
                "REPROCI_RESULT_FILE": "/output/tests.json",
                "TMPDIR": "/tmp",
            },
            labels={"reproci.job": job_id, "reproci.attempt": attempt_id},
            detach=True,
        )
        container.start()
        stop_reason = None
        while True:
            container.reload()
            if container.status == "exited":
                break
            if cancelled():
                container.kill()
                stop_reason = "Cancelled"
                break
            if time.monotonic() - started > timeout:
                container.kill()
                stop_reason = "Attempt timed out"
                break
            time.sleep(0.4)
        container.reload()
        exit_code = container.attrs["State"].get("ExitCode")
        stdout = container.logs(stdout=True, stderr=False)
        stderr = container.logs(stdout=False, stderr=True)
        maximum = max_log_bytes or settings.max_log_bytes
        truncation = {
            "stdout": write_bounded(output / "stdout.log", stdout, maximum),
            "stderr": write_bounded(output / "stderr.log", stderr, maximum),
        }
        tests_path = output / "tests.json"
        tests = json.loads(tests_path.read_text()) if tests_path.exists() else []
        if not isinstance(tests, list):
            tests = []
        outcome = (
            ("cancelled" if stop_reason == "Cancelled" else "error")
            if stop_reason
            else classify(exit_code, tests)
        )
        return {
            "outcome": outcome,
            "exit_code": exit_code,
            "tests": tests,
            "truncation": truncation,
            "container_id": container.id,
            "error": stop_reason
            or (None if outcome != "error" else "Pytest did not produce valid test results"),
        }
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass
        client.close()
