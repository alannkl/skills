# Production Operations Review Overlay

Use this overlay when a change affects reliability, background jobs, queues, schedulers, external services, retries, timeouts, migrations, observability, incident response, or high-volume paths.

## Review Focus

- Failure modes: check partial failure, dependency outage, network errors, retry storms, duplicate delivery, poison messages, clock skew, and resource exhaustion. For a batch or loop, trace a case where one item succeeds and a later item fails: what happens to the first item's retry, delivery, loss, or duplication.
- Timeouts and retries: verify explicit timeouts, bounded retries, backoff, jitter, cancellation, idempotency, and whether retry behavior amplifies load. Compose the serial calls, retries, and fallback endpoints along the critical path and compare the worst case against the enclosing deadline, lease, lock, or freshness window.
- Data volume and scaling: check query shape, pagination, batching, N+1 calls, memory growth, file size assumptions, cache pressure, and hot-path complexity.
- Background work: check job uniqueness, deduplication, locking, ordering, concurrency limits, dead-letter handling, and resume behavior after crash or deploy. For a shared resource, construct two operations that overlap between validation and action. For a proof assembled from several reads, verify that the reads come from sources and states that can validly support the combined conclusion, and that the code revalidates when an intervening change can invalidate it.
- Observability: verify logs, metrics, traces, audit events, correlation IDs, and error context are enough to diagnose failures without leaking sensitive data.
- Rollout and rollback: check feature flags, config defaults, migration sequencing, mixed-version behavior, and whether rollback leaves data or queues in a usable state.
- Degraded behavior: check fallbacks, circuit breakers, rate limits, backpressure, user-visible errors, and cleanup of temporary resources.
- Tests and checks: prefer integration tests for failure paths, migration tests, load-sensitive smoke checks, and targeted instrumentation checks when feasible.

## Common Findings

- External calls run without timeouts or cancellation in request paths.
- Retry logic is unbounded or retries non-idempotent writes.
- A migration or job assumes all data fits in memory.
- Errors are swallowed or logged without enough identifiers to find the affected operation.

Report operational risk when it has a concrete production trigger, not merely because a system could be more observable or scalable in the abstract.
