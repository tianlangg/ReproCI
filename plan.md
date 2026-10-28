# ReproCI: implementation plan and specification

## 1. Purpose and scope

ReproCI is a small CI engine that runs pytest jobs in fresh Docker containers, records results in PostgreSQL, and helps explain failures. Build it for Python repositories you own and use a deliberately broken demo repository to demonstrate the debugging features.

A recruiter should be able to clone the project, follow the README, and see two jobs running concurrently, a stored test failure, an isolated replay, a flaky-test report, and the commit that introduced a regression.

**Status:** This document specifies planned behavior. A feature is complete only when its acceptance checks pass. The resume currently describes the project in the past tense; treat every listed capability as a delivery requirement before presenting it as implemented.

### Scope limits

- One developer, one Linux host or Docker Desktop installation, one PostgreSQL database.
- Python and pytest only; trusted, explicitly registered repositories only.
- CLI plus FastAPI endpoints and generated Markdown reports. FastAPI's interactive API documentation provides an inspection interface.
- Default concurrency: two independent job containers. Each job runs one pytest invocation, without pytest-xdist.
- GitHub push webhooks only. Pull requests, public multi-user hosting, dashboards, Kubernetes, Redis, Celery, coverage analysis, and arbitrary build languages are outside version 1.
- ReproCI's own GitHub Actions workflow tests the engine. It is separate from the engine that runs submitted jobs.

## 2. Resume requirements and proof

The resume's two ReproCI bullets are the source of the required features.

> Built a containerized CI execution engine with parallel Docker workers, asynchronous job scheduling, and PostgreSQL-backed test tracking to accelerate automated testing.

> Implemented automated regression localization using Git bisect and isolated test replay; integrated GitHub webhooks and flaky-test detection to streamline CI debugging.

| Resume claim | Smallest complete implementation | Evidence to show |
| --- | --- | --- |
| Containerized CI engine | Engine service and PostgreSQL start with Docker Compose; test code executes in separate disposable containers | One-command startup, completed demo job, retained logs |
| Parallel Docker workers | Scheduler launches up to two job containers concurrently | Overlapping start/end timestamps and benchmark results |
| Asynchronous scheduling | API persists requests immediately; separate asyncio scheduler claims queued work and supervises containers | Two running jobs, a third queued job, responsive API |
| PostgreSQL-backed test tracking | Durable runs, attempts, individual test outcomes, and job events | Results still available after service restart |
| Faster automated testing | Compare the same batch at concurrency one and two | Measured wall times and calculated speedup, with hardware and workload stated |
| Git bisect localization | Replay one selected test across a known good-to-bad commit range using actual Git bisect | Known injected regression commit correctly identified |
| Isolated test replay | New checkout and fresh container rerun an exact pytest node ID at an exact commit | Replay links to original attempt and records its own outcome |
| GitHub webhooks | Verified push event for a registered repository creates one run | Real delivery ID, accepted event, persisted run, duplicate ignored |
| Flaky-test detection | Repeated isolated runs of the same test under the same recorded inputs detect mixed pass/fail results | Attempt-level evidence and an explicit mixed-outcome label |

Do not invent a performance number or call every intermittent failure a flaky test.

## 3. Main user workflow

1. Start the engine and database with `docker compose up --build`.
2. Register the included demo repository with its allowed branch, test image, and test configuration.
3. Submit its exact commit SHA through the CLI.
4. Scheduler claims the run, creates a clean checkout, and launches a test container.
5. Inspect the run summary and individual failing test IDs.
6. Replay one test, request repeated replays, or start a bisect investigation.
7. Export a Markdown report containing commit IDs, outcomes, logs, and debugging evidence.

These are intended CLI commands, to be implemented in this project:

```bash
reproci repo add demo --url <demo-repository-url> --branch main
reproci run demo --commit <full-sha>
reproci status <run-id>
reproci tests <run-id>
reproci replay <attempt-id> --test tests/test_total.py::test_total
reproci flakes <attempt-id> --test tests/test_total.py::test_total --repeats 10
reproci bisect <attempt-id> --good <good-sha> --bad <bad-sha> --test tests/test_total.py::test_total
reproci report <run-id> --output report.md
```

## 4. Architecture in plain language

Use three long-running services: API, scheduler, and PostgreSQL. The scheduler creates short-lived Docker containers, called workers, to execute tests. A worker slot means one running test container, not another queue service.

| Component | Responsibility | Must not do |
| --- | --- | --- |
| FastAPI API | Validate requests; save jobs; return IDs and query results | Run tests inside the HTTP request |
| Async scheduler | Claim jobs; enforce concurrency; create containers; persist outcomes | Execute repository code in its own process |
| Docker test container | Run pytest for one attempt and write results | Access engine credentials or the Docker socket |
| PostgreSQL | Store the queue and durable execution records | Store large console logs |
| Artifact volume | Keep checkout directories, JUnit XML, bounded logs, and reports | Serve as the only record of job status |
| CLI | Call API and present readable summaries | Duplicate scheduling logic |

Suggested stack: Python, FastAPI, asyncio, SQLAlchemy with psycopg, Alembic, PostgreSQL, Docker SDK, pytest, argparse, and GitHub Actions. Use ordinary functions and a small number of modules. Pin dependency versions in a lockfile when implementation begins.

### Container and volume layout

- Only the scheduler receives the Docker socket. This makes the scheduler a trusted host-level component.
- Compose creates a named artifact volume shared with the scheduler. Mount that same volume into each child container at `/work`, using an explicit configured Docker volume name.
- Each attempt receives a unique directory. Mount only its source directory read-only at `/src` and its output directory writable at `/output`. Use a private writable container directory for temporary files and Python caches.
- Build one fixed demo test image from a pinned base image and locked dependencies. Record its resolved image ID for every attempt and retain it for replay.
- Runtime test containers have no network, no secrets, no Docker socket, dropped capabilities, a non-root user, and explicit CPU, memory, PID, and time limits.
- Docker is execution isolation for trusted demo code, not a complete security boundary for arbitrary public submissions.

The repository is a small pure-Python package that can be imported from `/src`. Do not implement arbitrary install scripts. Dependency changes require registering a new image; bisection initially supports only histories compatible with one fixed dependency image.

## 5. Core execution specification

### Job states

Use `queued`, `running`, `passed`, `failed`, `error`, and `cancelled`.

- `failed`: pytest produced a valid test failure.
- `error`: setup, collection, image lookup, malformed output, timeout, or infrastructure prevented a trustworthy result.
- `cancelled`: explicit cancellation, with any running container stopped before releasing its slot.
- Preserve pytest's detailed per-test outcome separately from the overall job state.

Transitions: `queued -> running -> passed | failed | error | cancelled`; a queued job may also become cancelled. Terminal states do not change. A retry creates a new attempt rather than overwriting history.

### Scheduling

1. API inserts a queued job and returns HTTP 202 with its ID.
2. Scheduler polls PostgreSQL, initially every second.
3. Claim one eligible row using a short transaction with `SELECT ... FOR UPDATE SKIP LOCKED`; set ownership and running state before committing.
4. Keep at most `MAX_CONCURRENT_JOBS` active tasks, default two. Do not claim work unless a slot is available.
5. Use asyncio tasks for orchestration and `asyncio.to_thread` around blocking Docker operations. Never keep a database transaction open while a container runs.
6. Give each container labels containing its job ID and attempt ID. Update a heartbeat while supervising it.
7. On scheduler restart, inspect stale running jobs and their labeled containers, stop any leftovers, and mark interrupted attempts as errors. Require an explicit retry. Also remove orphaned labeled containers.

Version 1 runs one scheduler. Row locks prevent duplicate claims, but do not claim distributed scheduling or exactly-once execution. Duplicate webhook delivery prevention is a separate database guarantee.

### Executing a test

- Resolve and validate the full commit SHA against the registered repository and branch. Fetch repository data outside the test container; never execute checked-out code while fetching.
- Produce a clean checkout with no previous run's untracked files. Disable submodules and Git hooks for this workflow.
- Record the source SHA, exact image ID, command argument list, selected tests, supported environment settings, resource limits, and engine version.
- Invoke pytest with argument lists rather than shell interpolation, writing JUnit XML to `/output/junit.xml`.
- Retain an exact pytest node ID in every test record, including parameterized IDs. Use a small pytest plugin to write a JSON sidecar containing node IDs and setup/call/teardown outcomes; JUnit alone is insufficient for reliable node ID reconstruction.
- Capture stdout/stderr to bounded files, default 5 MiB each, with truncation noted. Record exit code, duration, and timestamps.
- Treat pytest exit 1 with valid failure records as failed. Exit 0 with valid results is passed. Collection/internal/usage errors and no collected tests are errors. Preserve skipped and xfail details; do not classify setup errors as ordinary assertion failures.
- Default timeout: 120 seconds per attempt. Stop and remove the container on timeout or cancellation. Persist error details even if reports are missing.

## 6. Data model

Keep large artifacts on disk and normalized metadata in PostgreSQL. Use Alembic migrations from the first milestone.

| Table | Key fields |
| --- | --- |
| `repositories` | ID, unique name, exact allowed remote URL, allowed branch, test image ID, default pytest arguments, config version |
| `webhook_deliveries` | Unique GitHub delivery ID, event type, payload hash, repository ID, received time, associated run ID or ignored reason |
| `runs` | ID, repository ID, commit SHA, branch, trigger, creation time, webhook delivery reference |
| `jobs` | ID, run ID, kind (`suite`, `replay`, `flake`, `bisect`), state, owner, heartbeat, request parameters, timestamps |
| `attempts` | ID, job ID, parent attempt ID, tested SHA, exact image ID, command, environment fingerprint, outcome, exit code, timing, artifact paths, container ID |
| `test_results` | Attempt ID, exact node ID, phase outcomes, duration, failure summary |
| `investigations` | ID, job ID, source attempt ID, test node ID, good/bad SHAs, final classification, first bad SHA, explanation |
| `job_events` | Job ID, event type, timestamp, short message |

Add foreign keys, a unique `(attempt_id, node_id)` test key, and indexes on queue state/creation time and test history. One normal suite job has one attempt. A flake or bisect job has multiple child attempts and holds one scheduler slot while running them sequentially.

Store full execution manifests in the attempt metadata and artifacts. Fingerprint the immutable configuration with SHA-256 over canonical JSON. Never store secrets in manifests.

## 7. Isolated replay

Replay means rerunning the selected test, not rerunning the whole original suite.

- Input: original attempt ID and a node ID actually collected by that attempt.
- Reuse its exact source SHA, retained image ID, pytest configuration, allowed environment, and limits.
- Create a fresh checkout and container with the source attempt recorded as parent.
- Return the new outcome, logs, and a statement that a single-test replay may remove test-order interactions.
- If the image is missing, return an explicit unavailable-environment error. Do not silently use a newer image.
- Missing tests, unsupported manifests, and runtime errors remain errors, not passes.

Acceptance: reproduce a known deterministic failure in a clean container; rerun a passing test successfully; confirm neither sees files left by earlier attempts.

## 8. Flaky-test detection

A test is observed flaky when repeated attempts at the same commit and recorded environment produce both a valid pass and a valid test failure.

- Run ten sequential isolated replays by default, configurable from two to twenty.
- Group evidence by repository, commit SHA, image ID, configuration fingerprint, and exact test ID.
- Classifications: `observed_flaky`, `all_passed`, `all_failed`, or `inconclusive`. Errors are reported separately; infrastructure errors alone do not establish flakiness.
- Display pass/fail/error counts, failure messages, and every attempt ID. Ten passes mean no flakiness observed in ten attempts, not proof that a test is stable.
- Keep detection at a fixed commit. A passing older commit and failing newer commit indicate possible regression, not flakiness.
- The demo includes an intentionally intermittent fixture with recorded seed inputs. A separate controlled test checks mixed-outcome classification without relying on luck. Disclose that the fixture is synthetic.

Acceptance: mixed valid outcomes produce observed_flaky; all passes and all failures remain distinct; pass plus timeout is inconclusive rather than flaky.

## 9. Automated regression localization

Bisect asks: between a known passing commit and failing commit, which commit first made this test fail?

### Preconditions

- Both SHAs belong to the registered repository. Good must be an ancestor of bad.
- Version 1 accepts a linear history within that range; reject merge-containing ranges with a clear explanation.
- The same test node ID exists at both endpoints. The fixed image supports all candidate commits.
- Verify good passes and bad fails in three isolated runs each. Mixed endpoint outcomes stop the investigation as inconclusive.
- Limit an investigation to 50 candidate executions and 15 minutes by default.

### Algorithm

1. Create a dedicated checkout for the investigation and run actual `git bisect start <bad> <good>`.
2. For each candidate selected by Git, create a fresh source checkout and run only the selected test in the retained image.
3. Repeat each candidate three times. All passes mean good; all valid failures mean bad. Mixed outcomes stop as inconclusive. Infrastructure errors or missing tests mean skip.
4. Feed the classification to `git bisect good`, `git bisect bad`, or `git bisect skip`.
5. Save each candidate SHA and linked attempts. Accept a first bad commit only when Git identifies one unambiguously.
6. Recheck the reported commit and its immediate parent using the same test. If confirmation fails, report inconclusive.
7. Run `git bisect reset` and remove the investigation checkout in cleanup, including on cancellation.

Use subprocess argument arrays, timeouts, and captured Git output. Do not equate every nonzero process exit with a regression. If skipped commits prevent a unique answer, show the candidate set and limitation.

The result establishes the first observed test-breaking commit under this environment and monotonic-history assumption. It does not diagnose the faulty line or prove causation. Fix-then-break histories are outside the initial guarantee.

Acceptance: in a synthetic linear history of at least eight commits, find the injected regression; reject reversed or unrelated endpoints; handle a missing test and skipped commits without fabricating a result.

## 10. GitHub push integration

- Endpoint: `POST /webhooks/github`.
- Verify `X-Hub-Signature-256` with HMAC-SHA256 over raw request bytes and a constant-time comparison before parsing the event.
- Set a payload size limit. Validate delivery ID, event type, repository identity, allowed branch, and commit SHA. Reject invalid signatures.
- Accept push events on the configured branch. Ignore branch deletion, unsupported events, unregistered repositories, and other branches with a recorded reason.
- Map the payload repository to the registered remote URL. Do not clone arbitrary payload URLs.
- In one transaction insert the unique delivery and its queued run/job. A duplicate delivery returns the existing result without scheduling again.
- Return promptly after persistence. A webhook success confirms receipt, not a passing test run.
- Keep the API bound to localhost. For a real GitHub demonstration, expose only the webhook route through a temporary tunnel or protected proxy; do not expose job-control endpoints.
- Version 1 uses a public demo repository to avoid private-repository credential handling. GitHub status checks and PR comments are optional future work.

Acceptance: invalid signatures fail; signed push creates one run; redelivery creates none; ignored branches create none; one actual GitHub delivery is demonstrated in addition to synthetic fixtures.

## 11. API surface

| Method and path | Behavior |
| --- | --- |
| `GET /health` | Report API/database readiness |
| `POST /repositories` | Register a trusted demo repository configuration |
| `POST /runs` | Queue exact-SHA suite run; return ID and 202 |
| `GET /runs` | Paginated recent runs |
| `GET /runs/{id}` | State, manifest, attempt summary, artifact references |
| `GET /runs/{id}/tests` | Individual tests and their outcomes |
| `POST /attempts/{id}/replay` | Queue isolated selected-test replay |
| `POST /attempts/{id}/flakes` | Queue repeated selected-test replay |
| `POST /attempts/{id}/bisect` | Queue regression investigation |
| `GET /jobs/{id}` | Job progress, child attempts, investigation result |
| `POST /jobs/{id}/cancel` | Cancel queued/running work |
| `GET /runs/{id}/report` | Download a Markdown evidence report |
| `POST /webhooks/github` | Verify and persist supported push delivery |

Validate inputs with Pydantic. IDs and artifact paths returned to clients must not allow arbitrary filesystem reads. Local-only administration avoids building accounts and authentication in version 1.

## 12. Repository layout

```text
reproci/
  README.md
  plan.md
  pyproject.toml
  dependency lockfile
  compose.yaml
  Dockerfile
  alembic.ini
  migrations/
  src/reproci/
    api.py
    cli.py
    config.py
    db.py
    models.py
    scheduler.py
    runner.py
    pytest_plugin.py
    results.py
    replay.py
    flakes.py
    bisect.py
    webhooks.py
    reports.py
  tests/
    unit/
    integration/
    end_to_end/
  demo/
    Dockerfile
    requirements.lock
    create_history.py
    README.md
  scripts/
    benchmark.py
  docs/
    architecture.md
    demo.md
  .github/workflows/ci.yml
```

Keep the test-bearing demo repository separate from engine code. `create_history.py` builds the reproducible local fixture history for automated tests; publish a corresponding public demo repository for the real webhook demonstration.

## 13. Build sequence and milestone gates

These are implementation phases, not a fixed deadline. Finish one working vertical slice before adding the next.

### M1: One suite in one container

Build a CLI or direct runner function that accepts a demo checkout, starts its fixed test image, and produces logs, JSON test metadata, and JUnit XML. Add resource limits, timeout handling, and cleanup immediately.

**Gate:** a passing test, failing test, collection error, and timeout each produce the correct outcome. Containers are removed after every case.

### M2: Persistence and API

Add PostgreSQL, migrations, repositories, runs, jobs, attempts, test results, and the submission/query endpoints. Return durable IDs. Start with serial execution.

**Gate:** submit a run, inspect individual tests, restart services, and retrieve the same results and artifacts.

### M3: Async queue and two workers

Move execution into the separate scheduler. Add safe claiming, two worker slots, events, heartbeat recovery, and cancellation.

**Gate:** queue three jobs; observe two running and one queued; each claimed job gets one attempt; API stays responsive; scheduler restart stops leftovers and reports interrupted work.

### M4: Isolated replay

Persist immutable manifests and implement selected-test replay with a new checkout and container.

**Gate:** replay uses the original SHA and image, links to its parent, and cannot read an earlier attempt's output.

### M5: Flaky detection

Build repeated replay on top of M4, with fixed-input grouping and explicit inconclusive outcomes.

**Gate:** stable pass, stable failure, controlled mixed outcomes, and infrastructure errors produce the specified classifications.

### M6: Git bisect

Add endpoint validation, isolated candidate execution, actual Git bisect interaction, skipped-commit handling, result confirmation, and budgets.

**Gate:** find the known injected commit and show its parent passes; ambiguous or flaky inputs do not produce a false first-bad claim.

### M7: Webhooks and GitHub Actions

Implement signed push intake and transactional deduplication. Add engine CI that runs formatting/lint checks, unit tests, and a small real-Docker/PostgreSQL integration suite on a compatible Linux runner.

**Gate:** real signed push creates a run, redelivery does not, invalid signature fails, and engine CI is green. Use real Docker for runner checks, not only mocks.

### M8: Benchmark and recruiter presentation

Complete CLI commands, Markdown reporting, architecture documentation, and the short demo. Measure concurrency benefits on the same machine with the same test inputs.

**Gate:** every resume requirement in section 2 has a reproducible demonstration and a link from the README.

## 14. Validation strategy

Write tests for behavior at boundaries, particularly places where the engine could report a false result.

| Layer | Required checks |
| --- | --- |
| Unit | Outcome classification, exact node IDs including parameters, manifest fingerprints, flaky classification, signature verification, bisect verdict mapping |
| Database integration | Unique webhook delivery, transaction rollback, queue claims from competing database connections, restart persistence |
| Docker integration | Fresh execution, assertion failure vs collection error, timeout, bounded logs, cancellation, cleanup, unavailable image |
| Debugging integration | Exact isolated replay, known bisect history, missing test, ambiguous skips, flaky endpoint |
| End to end | API submission through scheduler to stored tests and downloadable report; two concurrent containers; signed push intake |

The GitHub Actions workflow must test ReproCI itself. Running pytest on a toy repository without testing scheduler/result handling does not demonstrate the engine's correctness.

## 15. Performance evidence

Benchmark throughput, meaning time to finish a batch, rather than claiming a single test runs faster.

- Submit eight identical demo suite jobs with deliberate independent work, such as a two-second wait in each suite. Disclose that this is a synthetic scheduling workload.
- Compare concurrency one against concurrency two using identical commits, image, limits, and hardware.
- Build images and fetch the repository beforehand. Report that image build and initial fetch are excluded; container startup, checkout preparation, execution, and result persistence remain included.
- Measure wall time from batch submission to all jobs reaching terminal state. Run at least five repetitions per mode and alternate modes to reduce ordering bias.
- Report median time, range, success counts, and speedup = serial median / parallel median. Record CPU, memory, Docker version, worker limit, and workload.
- Include one representative real pytest suite if available. Parallel CPU-heavy jobs can contend for resources; report the measured result even if improvement is small.
- Save the raw CSV and generated summary. Add a numeric resume speedup only after measuring it.

## 16. Recruiter-facing deliverables

The README should let a reviewer understand the project within a minute and run the core demo with a short sequence of commands.

- A concise problem statement: CI identifies failures; ReproCI adds repeatable execution and evidence for debugging them.
- One architecture diagram showing API, PostgreSQL queue, scheduler, job containers, and artifacts.
- Exact prerequisites, startup commands, demo commands, expected output, and teardown instructions. Keep destructive volume deletion separate from ordinary shutdown.
- A 60-90 second recording showing parallel jobs, a stored failure, a replay, and a known first bad commit. Show the flaky report and webhook delivery in a follow-up example if needed.
- A checked-in example report with real attempt IDs, test IDs, commit SHAs, outcomes, and measured benchmark data.
- Passing CI and a short limitations section covering trusted-code execution, fixed dependency images, observed flakiness, and linear/monotonic bisect assumptions.

## 17. Final completion checklist

- [ ] Engine and database start from documented Docker Compose commands.
- [ ] Two independent test containers execute concurrently, with bounded resource usage.
- [ ] Requests queue asynchronously and remain inspectable while execution is active.
- [ ] PostgreSQL retains runs, attempts, individual test outcomes, and investigation history.
- [ ] Timeouts, restarts, and cancellations leave explicit outcomes and no orphaned containers.
- [ ] A selected test replays at its original commit and exact retained image in a fresh environment.
- [ ] Actual Git bisect finds and confirms the demo's first test-breaking commit.
- [ ] Flaky detection presents mixed outcomes at fixed recorded inputs without confusing infrastructure errors with test failures.
- [ ] A real signed GitHub push schedules work and duplicate delivery is harmless.
- [ ] GitHub Actions validates the engine with meaningful unit and integration coverage.
- [ ] Serial/parallel benchmark numbers are measured, reproducible, and accurately described.
- [ ] README, report, and demo make every resume claim independently inspectable.

Stop adding features once these checks pass. A complete, explainable execution-and-debugging loop is the intended project.
