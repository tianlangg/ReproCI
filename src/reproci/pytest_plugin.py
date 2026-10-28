"""Copied into each test container; records exact pytest node IDs and phase reports."""

import json
import os

_records = {}


def pytest_runtest_logreport(report):
    row = _records.setdefault(
        report.nodeid, {"node_id": report.nodeid, "phases": {}, "duration": 0.0, "failure": None}
    )
    row["phases"][report.when] = report.outcome
    row["duration"] += report.duration
    if report.failed:
        row["failure"] = str(report.longrepr)[:4000]
    if hasattr(report, "wasxfail"):
        row["phases"]["xfail"] = str(report.wasxfail)


def pytest_sessionfinish(session, exitstatus):
    path = os.environ.get("REPROCI_RESULT_FILE", "/output/tests.json")
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(list(_records.values()), stream)
