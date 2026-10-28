import hashlib
import json


def fingerprint(manifest: dict) -> str:
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def classify(exit_code: int | None, tests: list[dict], *, timed_out=False) -> str:
    if timed_out or not tests or exit_code not in (0, 1):
        return "error"
    if any(
        t.get("phases", {}).get("setup") == "failed"
        or t.get("phases", {}).get("teardown") == "failed"
        for t in tests
    ):
        return "error"
    failures = [t for t in tests if t.get("phases", {}).get("call") == "failed"]
    if exit_code == 1 and failures:
        return "failed"
    if exit_code == 0 and not failures:
        return "passed"
    return "error"


def flake_classification(outcomes: list[str]) -> str:
    valid = [o for o in outcomes if o in ("passed", "failed")]
    if "passed" in valid and "failed" in valid:
        return "observed_flaky"
    if len(valid) != len(outcomes):
        return "inconclusive"
    if valid and all(o == "passed" for o in valid):
        return "all_passed"
    if valid and all(o == "failed" for o in valid):
        return "all_failed"
    return "inconclusive"
