"""Run the same eight-job synthetic workload at one and two worker slots."""

import argparse
import csv
import json
import platform
import statistics
import subprocess
import time
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:18743")
    parser.add_argument("--repository", default="demo")
    parser.add_argument("--image", default="reproci-demo-test:local")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("examples/benchmark.csv"))
    args = parser.parse_args()
    rows = []
    with httpx.Client(base_url=args.api, timeout=20) as api:
        for repetition in range(args.repetitions):
            for concurrency in (1, 2) if repetition % 2 == 0 else (2, 1):
                env = __import__("os").environ.copy()
                env["REPROCI_MAX_CONCURRENT_JOBS"] = str(concurrency)
                env["REPROCI_PORT"] = args.api.rsplit(":", 1)[-1]
                subprocess.run(
                    ["docker", "compose", "up", "-d", "--force-recreate", "scheduler"],
                    check=True,
                    env=env,
                    stdout=subprocess.DEVNULL,
                )
                start = time.monotonic()
                jobs = []
                for _ in range(8):
                    response = api.post(
                        "/runs", json={"repository": args.repository, "commit": args.commit}
                    )
                    response.raise_for_status()
                    jobs.append(response.json()["job_id"])
                deadline = start + 300
                while time.monotonic() < deadline:
                    states = [api.get(f"/jobs/{job_id}").json()["state"] for job_id in jobs]
                    if all(state in ("passed", "failed", "error", "cancelled") for state in states):
                        break
                    time.sleep(0.25)
                else:
                    raise RuntimeError("Benchmark batch timed out")
                seconds = time.monotonic() - start
                row = {
                    "repetition": repetition + 1,
                    "concurrency": concurrency,
                    "seconds": round(seconds, 3),
                    "passed": states.count("passed"),
                    "failed": states.count("failed"),
                    "error": states.count("error"),
                }
                rows.append(row)
                print(row, flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    serial = [r["seconds"] for r in rows if r["concurrency"] == 1]
    parallel = [r["seconds"] for r in rows if r["concurrency"] == 2]
    summary = {
        "workload": "eight identical suites with a two-second sleep; synthetic scheduling workload",
        "measurement_boundary": "Batch submission through all terminal results. Image build and initial repository creation excluded; checkout, container start, execution, and persistence included.",
        "commit": args.commit,
        "host": platform.platform(),
        "cpu": platform.processor(),
        "docker_resources": subprocess.check_output(
            ["docker", "info", "--format", "CPUs={{.NCPU}} MemoryBytes={{.MemTotal}}"],
            text=True,
        ).strip(),
        "image_id": subprocess.check_output(
            ["docker", "image", "inspect", args.image, "--format", "{{.Id}}"], text=True
        ).strip(),
        "docker": subprocess.check_output(
            ["docker", "version", "--format", "{{.Server.Version}}"], text=True
        ).strip(),
        "serial_median": statistics.median(serial),
        "serial_range": [min(serial), max(serial)],
        "parallel_median": statistics.median(parallel),
        "parallel_range": [min(parallel), max(parallel)],
        "speedup": round(statistics.median(serial) / statistics.median(parallel), 2),
        "raw_csv": str(args.output),
    }
    args.output.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
