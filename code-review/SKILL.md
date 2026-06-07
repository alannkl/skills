---
name: code-review
description: Produce high-signal code review reports focused on intent fit, correctness, security, maintainability, tests, and operational risk. Use when the user asks for code review, PR review, diff review, pre-merge review, bug-risk review, or findings on changed code; do not use for implementation, prose editing, pure design critique, or architecture brainstorming without concrete code to review.
---

# Code Review

## Purpose

Review code to protect behavior, contracts, users, operators, and future maintainers. Produce a concise report of real issues, their impact, and proposed fixes or next steps.

## Core Philosophy

- Review with principal-engineer judgment: reason from first principles, question assumptions that affect behavior or risk, and look for subtle bugs, performance traps, and concrete maintenance risks.
- Reconstruct the change intent before judging code. Use the stated goal when available; otherwise infer intent from the code changes and surrounding system behavior.
- Validate intent when code or context raises doubt: ask whether the inferred or stated goal fits existing system design, business rules, and user-facing contracts.
- Scope review to the requested selection, branch, PR, files, or current diff. Avoid unrelated legacy findings unless the change triggers or worsens them.
- Correctness, security, regressions, data integrity, and contract safety outrank style and preference.
- Respect repository rules, project architecture, framework conventions, and user instructions over generic advice.
- Report only concrete, actionable, high-confidence issues. Prefer a few defensible findings over broad commentary.
- Every finding must explain the problem, why it matters, and a specific proposed fix or next step.

## Workflow

1. Establish scope and intent.
   - State what is being reviewed and what appears out of scope.
   - Gather relevant user goals, issue context, PR description, local rules, architecture notes, and nearby tests.
   - If intent is missing, infer it from the code change, affected call sites, tests, names, and surrounding behavior; label it as an assumption, not a fact.
   - When the code appears to implement the wrong behavior, check the inferred or stated intent against existing system and business logic before reviewing implementation mechanics.

2. Read enough context.
   - Inspect changed files, directly related tests, called functions, imported modules, neighboring code, and contract-defining files as needed.
   - Identify public surfaces touched by the change: APIs, CLI flags, config, schemas, migrations, events, persisted data, permissions, external integrations, and serialized formats.
   - For generated or mechanical diffs, verify the generator, source rule, or representative output instead of line-reviewing noise.

3. Review by risk, not file order.
   - Intent fit: does the change implement a logical, system-aligned behavior without scope drift or missing cases?
   - Functional correctness: boundary conditions, edge cases, missing branches, null/error handling, off-by-one mistakes, state transitions, concurrency, idempotency, and resource lifecycle.
   - Breaking changes: backward/forward compatibility, mixed-version behavior, migration paths, defaults, rollback, and external integrations.
   - Security and privacy: authorization, input validation, injection, secrets, sensitive logging, personal data, dependency risk, and least privilege.
   - Data integrity: old data, partial writes, transaction boundaries, retries, duplicate delivery, and failure recovery.
   - Performance and reliability: N+1 calls, data volume, algorithmic complexity, batching, caching, timeouts, retries, rate limits, observability, and cleanup.
   - Maintainability: unnecessary abstractions, duplicated logic, unclear boundaries, naming, large unfocused functions, and code that will be hard to change safely.
   - User-facing behavior: accessibility, loading/error/empty states, responsive behavior, platform compatibility, and internationalization when relevant.

4. Apply only relevant specialized overlays.
   - Use overlays for surfaces the change actually touches; do not run every checklist by default.
   - AI/agent systems: bounded prompt or context construction, hard caps on injected content, prompt-injection safety, session/resume compatibility, and large model-visible fragments that need manual review.
   - API/config/CLI/data contracts: compatibility, defaults, migrations, rollback, serialized formats, and external integration surfaces.
   - Security/privacy: changed trust boundaries, privilege escalation paths, secret handling, sensitive-data exposure, and least-privilege access.
   - Frontend/UI: accessibility, keyboard behavior, responsive layout, loading/error/empty states, and visible regressions.
   - Operations: observability, timeouts, retries, rate limits, resource cleanup, degraded behavior, and incident diagnosability.

5. Review tests deliberately.
   - Check whether changed behavior has meaningful tests at the right level.
   - Prefer behavior-level and integration coverage for cross-module behavior, workflows, external contracts, and agent logic.
   - Treat missing tests as a finding only when tied to real behavior risk.
   - Look for false confidence: brittle mocks, assertions that cannot fail, missing edge cases, nondeterminism, fixtures that hide the bug, or tests overfit to implementation details.
   - Run focused tests when feasible. If not run, state the gap.

6. Control review size.
   - Flag large non-mechanical diffs as reviewability risks when they are too broad to inspect reliably.
   - Use rough scrutiny thresholds: over about 800 changed lines for non-mechanical changes, or over about 500 changed lines for complex logic.
   - Suggest the smallest coherent stage based on real dependencies, affected call sites, and migration order.

7. Classify and filter findings.
   - `Critical`: exploitable security issue, data loss/corruption, system-breaking regression, broken public contract, or complete logic failure.
   - `High`: likely user-visible bug, severe regression, broken migration/rollback path, major performance issue, or explicit project-rule violation.
   - `Medium`: contained but real bug, missing validation, meaningful test gap, brittle logic likely to cause future defects, or maintainability issue with practical risk.
   - `Low`: minor cleanup with practical value; omit unless the user asks for exhaustive review.
   - Do not turn a guessed intent into a finding unless the code or surrounding context gives concrete evidence.
   - Do not report pure style opinions, praise, restatements of the code, vague "check/ensure/verify" chores, speculative issues without evidence, or broad rewrites when a local fix addresses the issue.

## Output Format

Start with findings ordered by severity. If there are no findings, say that clearly.

For each finding include:

- Severity and short title.
- File and line when available.
- Problem: the concrete issue.
- Why it matters: behavioral, user, security, operational, or maintainability impact.
- Proposed fix: a specific next step.

Then include:

- Open questions or assumptions.
- Tests or checks reviewed or run.
- Residual risks.
- Proposed next steps.

## Gotchas

- Do not turn review into a style pass unless style affects correctness, maintainability, or explicit project rules.
- Do not comment on unchanged code just because it is nearby.
- Do not ask the author to verify something the reviewer can inspect.
- Do not assume missing tests are always a blocker; tie the gap to behavior risk.
- Do not approve large risky diffs just because each line looks reasonable in isolation.
