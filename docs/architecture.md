# Architecture

The API stores requests as `queued` jobs. The scheduler polls PostgreSQL once
per second and claims only as many rows as it has worker slots, using
`FOR UPDATE SKIP LOCKED`. It commits the `running` state before fetching code
or starting Docker. Two asyncio tasks can supervise independent containers;
blocking Docker calls run in threads. No transaction stays open during a test.

For each attempt, the scheduler clones the registered remote, checks that the
full SHA is on the allowed branch, then removes Git metadata from a fresh source
directory. The test container mounts only that source subdirectory read-only
and its own output subdirectory writable from the named artifact volume. It
has no network, Docker socket, or database credentials. The image is resolved
to an immutable image ID before launch. CPU, memory, PID, and wall-time limits
bound each attempt.

The pytest plugin writes exact node IDs and setup/call/teardown phases. A valid
assertion failure is `failed`; collection errors, missing results, setup errors,
and timeouts are `error`. PostgreSQL stores outcomes and event history; the
volume stores JUnit XML and bounded console logs. On scheduler restart,
leftover labeled containers are removed and interrupted jobs become errors.

Replay uses the source attempt's SHA, image ID, and pytest configuration with
one selected node ID. Flake detection runs sequential replays and requires
both valid passes and valid failures for `observed_flaky`. Bisect verifies good
and bad endpoints three times, drives actual `git bisect`, and confirms the
reported commit plus its parent. Unstable or ambiguous evidence is inconclusive.

This version has one scheduler, one database, and localhost-only administration.
Row locks prevent duplicate claims but are not a distributed exactly-once
guarantee. Webhook delivery IDs have a separate unique database key.
