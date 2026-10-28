from reproci.results import classify, fingerprint, flake_classification
from reproci.webhooks import valid_signature
import hashlib
import hmac


def test_outcomes():
    passed = [{"node_id": "tests/test_x.py::test_x[1]", "phases": {"call": "passed"}}]
    failed = [{"node_id": "tests/test_x.py::test_x[1]", "phases": {"call": "failed"}}]
    setup = [{"node_id": "tests/test_x.py::test_x[1]", "phases": {"setup": "failed"}}]
    assert classify(0, passed) == "passed"
    assert classify(1, failed) == "failed"
    assert classify(1, setup) == "error"
    assert classify(5, []) == "error"
    assert classify(None, passed, timed_out=True) == "error"


def test_flakes():
    assert flake_classification(["passed", "failed"]) == "observed_flaky"
    assert flake_classification(["passed"] * 3) == "all_passed"
    assert flake_classification(["failed"] * 3) == "all_failed"
    assert flake_classification(["passed", "error"]) == "inconclusive"


def test_fingerprint_order_independent():
    assert fingerprint({"a": 1, "b": 2}) == fingerprint({"b": 2, "a": 1})


def test_signature():
    body = b'{"test":true}'
    signature = "sha256=" + hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    assert valid_signature(body, signature, "secret")
    assert not valid_signature(body + b"!", signature, "secret")
