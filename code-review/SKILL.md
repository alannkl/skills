---
name: code-review
description: Produce full, findings-led code review reports focused on intent fit, correctness, security, maintainability, tests, and operational risk. Use when the user asks for code review, PR review, diff review, pre-merge review, bug-risk review, or findings on changed code; do not use for implementation, prose editing, pure design critique, inline review comments, or architecture brainstorming without concrete code to review.
---

# Code Review

## Purpose

Review code to protect behavior, contracts, users, operators, and future maintainers. Produce a concise report of real issues, their impact, and a proposed fix or next step. Apply principal-engineer judgment: reason from first principles, question assumptions that affect behavior or risk, and hunt for subtle bugs, performance traps, and concrete maintenance risks.

## Core Principles

- Reconstruct the change intent before judging code. Use the stated goal when available; otherwise infer it from the code, call sites, tests, names, and surrounding behavior, and label the inference as an assumption.
- Validate intent when code or context raises doubt: does the inferred or stated goal fit existing system design, business rules, and user-facing contracts? If the implementation matches the stated request but violates existing contracts, frame the finding as an intent/system-contract conflict.
- Scope the review to the requested selection, branch, PR, files, or diff. Avoid unrelated legacy findings unless the change triggers or worsens them.
- Correctness, security, regressions, data integrity, and contract safety outrank style and preference.
- Respect repository rules, project architecture, framework conventions, and user instructions over generic advice.
- Report only concrete, actionable, high-confidence issues; prefer a few defensible findings over broad commentary. Every finding must explain the problem, why it matters, and a specific proposed fix or next step.

## Workflow

1. Establish scope and intent.
   - State what is being reviewed and what appears out of scope.
   - Gather goals and context, adapting to the repo's VCS and platform: the diff and its size against the merge target (e.g. `git diff <base>...HEAD`) and the PR/MR description (e.g. `gh`/`glab`); project guidance if present (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `CONTRIBUTING.md`, architecture docs, linter config).
   - If intent is missing, infer it and label it as an assumption, not a fact. When the code appears to implement the wrong behavior, check intent against existing system and business logic before reviewing mechanics.
   - If tooling is unavailable (no PR platform, detached/shallow checkout, commands fail), degrade gracefully: review what you can access, state which context you could not gather, and treat it as a residual risk rather than guessing.

2. Read enough context.
   - Inspect changed files, related tests, called functions, imported modules, neighboring code, and contract-defining files as needed.
   - Identify public surfaces touched: APIs, CLI flags, config, schemas, migrations, events, persisted data, permissions, external integrations, and serialized formats.
   - For generated or mechanical diffs, verify the generator, source rule, or representative output instead of line-reviewing noise.

3. Review by risk, not file order.
   - Intent fit: logical, system-aligned behavior without scope drift or missing cases.
   - Functional correctness: boundaries, edge cases, missing branches, null/error handling, off-by-one, state transitions, concurrency, race conditions, lock ordering, idempotency, resource lifecycle.
   - Breaking changes: backward/forward compatibility, mixed-version behavior, migrations, defaults, rollback, external integrations.
   - Security and privacy: authorization, input validation, injection, secrets, sensitive logging, personal data, dependency risk, least privilege.
   - Data integrity: old data, partial writes, transaction boundaries, retries, duplicate delivery, failure recovery.
   - Performance and reliability: N+1 calls, data volume, complexity, batching, caching, timeouts, retries, rate limits, backpressure, observability, cleanup.
   - Maintainability: unnecessary abstractions, duplicated logic, unclear boundaries, naming, large unfocused functions, code that is hard to change safely.

4. Apply specialized overlays only for touched surfaces that need deeper scrutiny beyond the Step 3 scan.
   - AI / agent systems: bounded prompt/context construction, hard caps on injected content, prompt-injection safety, session/resume compatibility, and manual review of large model-visible fragments.
   - Contract surfaces: for API, config, CLI, schema, migration, event, or serialized-format changes, check defaults, compatibility, rollback, client/server version skew, and external integration behavior.
   - Frontend / UI: accessibility, keyboard behavior, responsive layout, loading/error/empty states, and internationalization.
   - Trust boundaries: for authorization, secrets, personal data, dependency, or privilege changes, check escalation paths, exposure risk, least privilege, and auditability.
   - Production operations: for reliability-sensitive changes, check observability, timeouts, retries, rate limits, backpressure, cleanup, degraded behavior, incident diagnosability, and rollout safety.

5. Review tests deliberately.
   - Check whether changed behavior has meaningful tests at the right level; prefer behavior-level and integration coverage for cross-module behavior, workflows, external contracts, and agent logic.
   - Treat missing tests as a finding only when tied to real behavior risk.
   - Look for false confidence: brittle mocks, assertions that cannot fail, missing edge cases, nondeterminism, fixtures that hide the bug, or tests overfit to implementation.
   - Run focused tests when feasible. If not run, state the gap.

6. Control review size.
   - Flag large non-mechanical diffs as reviewability risks when too broad to inspect reliably.
   - Use rough scrutiny thresholds, adjusting to repo norms and change complexity: roughly over 800 changed lines for non-mechanical changes, or over 500 for complex logic.
   - Treat reviewability as a finding when the change structure blocks reliable review: unrelated changes bundled together, mechanical and semantic edits mixed without separation, generated output without the source rule or generator change, migrations mixed with behavior changes, or broad rewrites without a clear dependency chain.
   - Suggest the smallest coherent stage based on real dependencies, affected call sites, and migration order.

7. Classify and filter findings.
   - Calibrate severity by impact, likelihood, and confidence. Do not escalate a severe but unproven risk without evidence; report it at a lower severity with the assumption or uncertainty stated.
   - `Critical`: exploitable security issue, data loss/corruption, system-breaking regression, broken public contract, or complete logic failure.
   - `High`: likely user-visible bug, severe regression, broken migration/rollback path, major performance issue, or explicit project-rule violation.
   - `Medium`: contained but real bug, missing validation, meaningful test gap, brittle logic likely to cause future defects, or maintainability issue with practical risk.
   - `Low`: minor cleanup with practical value; omit unless the user asks for exhaustive review.
   - If there are no findings, say so directly; do not invent low-value findings to avoid an empty review.
   - **Do not report:** guessed intent without concrete evidence, pure style opinions, praise, restatements of the code, vague "check/ensure/verify" chores, speculative issues without evidence, or broad rewrites when a local fix addresses the issue.

## Output Format

Start with findings ordered by severity. Keep scope concise and place it after findings unless the user explicitly asks for a different format. If there are no findings, say so clearly (e.g. "No blocking issues found in the reviewed scope.") and still report scope, tests, and residual risks. Omit optional sections when they would be empty or irrelevant. Use this structure:

```markdown
## Findings

### [Critical] <short title>

- **File:** path/to/file.ext:42
- **Problem:** <the concrete issue>
- **Evidence:** <specific code path, failing case, example input, violated contract, or reasoning chain>
- **Why it matters:** <behavioral, user, security, operational, or maintainability impact>
- **Proposed fix:** <specific next step>

## Scope

<what was reviewed; what is out of scope; stated or inferred intent>

## Open questions / assumptions

- <inferred intent labeled as assumption, ambiguities to confirm>

## Tests / checks

- <tests reviewed or run, and the result; state gaps if not run>

## Residual risks

- <what remains uncertain or unverified>

## Next steps

- <smallest actionable review follow-ups for the code author>
```

## Finding Quality

Calibrate every finding to be concrete, evidence-backed, and tied to behavior risk: name the location, show the failing case, explain the impact, propose a specific fix. Severity should reflect impact, likelihood, and confidence. Review in the language and conventions present in the diff; the example below illustrates the _shape_ of a strong finding, not its domain.

Good finding (report it):

> **[High] Pagination drops the partial last page** — `src/lib/paginate.ts:24`
> **Problem:** `const pageCount = Math.floor(total / pageSize)` undercounts pages when there is a remainder: with `total = 101` and `pageSize = 25` it yields `4`, but the caller loops `page < pageCount` (pages `0..3`), so the final item is never returned.
> **Evidence:** The remainder case `total = 101`, `pageSize = 25` needs five pages (`0..4`), but `Math.floor(101 / 25)` produces `4`.
> **Why it matters:** Consumers silently lose the final partial page, breaking the documented "returns all items" contract.
> **Proposed fix:** Use `Math.ceil(total / pageSize)` and add a boundary test for the remainder case.

Bad findings (do not report):

- "Consider adding more tests here." — vague, no behavior tied to it.
- "This function is a bit long; you might refactor it." — preference with no concrete risk.
- "Ensure this handles errors correctly." — a "verify" chore the reviewer can check directly.
- "Nice clean implementation!" — praise, not a finding.
- "Line 12 sets `count = 0`." — restates the code without identifying an issue.

## Gotchas

- Do not turn review into a style pass unless style affects correctness, maintainability, or explicit project rules.
- Do not comment on unchanged code just because it is nearby.
- Do not ask the author to verify something the reviewer can inspect.
- Do not assume missing tests are always a blocker; tie the gap to behavior risk.
- Do not approve large risky diffs just because each line looks reasonable in isolation.
