import os
import hashlib
import hmac
import json
import subprocess
import time
import uuid
from pathlib import Path

import docker
import httpx


def sha(repo, revision):
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", revision], text=True
    ).strip()


def wait_job(client, job_id, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = client.get(f"/jobs/{job_id}").json()
        if data["state"] in {"passed", "failed", "error", "cancelled"}:
            return data
        time.sleep(0.5)
    raise AssertionError(f"Job {job_id} did not finish")


def test_suite_replay_bisect():
    suffix = uuid.uuid4().hex[:8]
    name = "ci-demo-" + suffix
    repo = Path(__file__).parents[2] / "demo" / "history"
    good, bad = sha(repo, "HEAD~4"), sha(repo, "HEAD")
    first_bad = sha(repo, "HEAD~3")
    docker_client = docker.from_env()
    image_id = docker_client.images.get("reproci-demo-test:ci").id
    docker_client.close()
    with httpx.Client(
        base_url=os.environ.get("REPROCI_API_URL", "http://127.0.0.1:18743"), timeout=10
    ) as api:
        assert api.get("/health").status_code == 200
        response = api.post(
            "/repositories",
            json={
                "name": name,
                "url": "file:///demo-history",
                "branch": "main",
                "image_id": image_id,
            },
        )
        assert response.status_code == 201, response.text
        response = api.post("/runs", json={"repository": name, "commit": bad})
        assert response.status_code == 202, response.text
        run_id, job_id = response.json()["run_id"], response.json()["job_id"]
        suite = wait_job(api, job_id)
        assert suite["state"] == "failed", suite
        attempt_id = suite["attempts"][0]["id"]
        retry_response = api.post(f"/jobs/{job_id}/retry")
        assert retry_response.status_code == 202
        retried = wait_job(api, retry_response.json()["job_id"])
        assert retried["state"] == "failed"
        assert retried["attempts"][0]["id"] != attempt_id
        assert retried["attempts"][0]["parent_attempt_id"] == attempt_id
        tests = api.get(f"/runs/{run_id}/tests").json()
        assert any(
            t["node_id"] == "tests/test_total.py::test_total" and t["phases"]["call"] == "failed"
            for t in tests
        )
        replay = api.post(
            f"/attempts/{attempt_id}/replay", json={"test": "tests/test_total.py::test_total"}
        )
        assert wait_job(api, replay.json()["job_id"])["state"] == "failed"
        investigation = api.post(
            f"/attempts/{attempt_id}/bisect",
            json={"test": "tests/test_total.py::test_total", "good": good, "bad": bad},
        )
        result = wait_job(api, investigation.json()["job_id"])
        assert result["investigation"]["first_bad_sha"] == first_bad, result
        assert "tests/test_total.py::test_total" in api.get(f"/runs/{run_id}/report").text

        body = json.dumps(
            {
                "repository": {"clone_url": "file:///demo-history"},
                "ref": "refs/heads/main",
                "after": bad,
            }
        ).encode()
        signature = "sha256=" + hmac.new(b"ci-secret", body, hashlib.sha256).hexdigest()
        headers = {
            "X-Hub-Signature-256": signature,
            "X-GitHub-Delivery": "ci-delivery-" + suffix,
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        }
        assert (
            api.post(
                "/webhooks/github",
                content=body,
                headers={**headers, "X-Hub-Signature-256": "sha256=bad"},
            ).status_code
            == 401
        )
        delivery = api.post("/webhooks/github", content=body, headers=headers)
        assert delivery.status_code == 200, delivery.text
        assert delivery.json()["run_id"]
        duplicate = api.post("/webhooks/github", content=body, headers=headers).json()
        assert duplicate["duplicate"] and duplicate["run_id"] == delivery.json()["run_id"]
        other_body = json.dumps(
            {
                "repository": {"clone_url": "file:///demo-history"},
                "ref": "refs/heads/other",
                "after": bad,
            }
        ).encode()
        other_headers = {
            **headers,
            "X-GitHub-Delivery": "ci-delivery-other-branch-" + suffix,
            "X-Hub-Signature-256": "sha256="
            + hmac.new(b"ci-secret", other_body, hashlib.sha256).hexdigest(),
        }
        ignored = api.post("/webhooks/github", content=other_body, headers=other_headers)
        assert ignored.json()["ignored_reason"] == "other branch"
        assert ignored.json()["run_id"] is None
