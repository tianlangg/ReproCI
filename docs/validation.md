# Validation record

Local validation on 2026-10-27 used Docker Desktop 29.8.2 on macOS arm64.

| Check | Observed result |
| --- | --- |
| Unit tests | 6 passed, including exact parameterized pytest IDs, false-flake boundaries, and reproducible demo SHAs |
| End-to-end test | 1 passed: API → PostgreSQL queue → Docker suite → stored tests → linked retry → replay → actual Git bisect → signed synthetic webhook and duplicate |
| Known regression | `fcb686a494ec4b61bb38ebc5e3356a13d725c778` found and parent confirmed passing; see [report](../examples/report.md) |
| Flaky fixture | 10 fresh attempts at one commit and image: 5 passed, 5 failed, 0 errors; classified `observed_flaky` |
| Parallel execution | Eight job timestamps show pairs overlapping; see [timestamps](../examples/concurrency.json) |
| Timeout | Job `f367cdd0-9858-4a46-a4d1-051a5fc98dbd` recorded `error` / `Attempt timed out`; labeled container absent afterward |
| Cancellation | Two running, one queued observed; running job `0e9eb909-3bed-4d16-be93-a71d1ebf2f20` and queued job `c329e72b-a6c0-445a-a3ac-24c8fcaf07d7` became `cancelled`; no labeled containers remained |
| Restart recovery | Job `8be5ed81-f32b-4810-8a3b-411e7d500046` became `error` / `Scheduler interrupted` after scheduler kill and restart; no labeled container remained |
| Throughput | Five batches per mode, all 80 jobs passed; 36.395 s serial median, 17.334 s two-worker median, 2.10× batch speedup. See [raw CSV](../examples/benchmark.csv). |
| Image build | Compose engine image built from hashed `requirements.lock`; demo image built from pinned base and package versions |

The signed webhook integration used a synthetic payload. A **real GitHub push
delivery** and a **screen recording** require a public demo repository, reachable
webhook URL, and GitHub access. They are not represented as completed evidence.
The local `gh` account was unauthenticated during validation.
