---
name: code-review
description: Produce a findings-led code review report for concrete code changes. Use when the user asks for a code review, PR review, or findings on a commit, branch, diff, or named files; not for implementing fixes or critiquing designs without code.
---

# Code Review

## Purpose

Review concrete code changes to protect behavior, contracts, users, operators, and future maintainers. Produce concise, findings-led reports that explain real problems, their impact, and a specific fix or next step.

Apply principal-engineer judgment: reconstruct intent, reason from evidence and first principles, and question assumptions that affect correctness.

## Core principles

- Prioritize correctness, security, regressions, data integrity, and contract safety over style and preference.
- Respect repository rules, project architecture, framework conventions, and user instructions over generic advice.
- Judge code quality through concrete risk: scoped changes, simple enough design, clear boundaries, explicit contracts, testable behavior, and verifiable outcomes. Project conventions are the local standard, but convention-aligned code can still be reported when it creates correctness, security, compatibility, data-integrity, operational, or maintainability risk.

## Workflow

1. Establish scope and intent.
   - Use the scope the user named. It may be a pull request, commit or range, branch against a base, diff, staged or unstaged work, or named files.
   - If the user supplies no scope, use the first non-empty of: staged changes; unstaged and untracked changes; commits ahead of the upstream (`@{upstream}..HEAD`); or the current branch against its merge base with the default branch.
   - Freeze the resolved scope before deep reading. Inventory outside it only to state exclusions; never absorb adjacent changes into the review.
   - Gather goals and context from the repo's VCS and platform: diff and size against the merge target, for example `git diff <base>...HEAD`; PR/MR description, for example via `gh` or `glab`; commit messages and the issues they reference (`#123`, `Closes #45`); and project guidance such as `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `CONTRIBUTING.md`, architecture docs, or linter config.
   - Determine the full review surface inside the resolved scope before deep reading: diff stat, file status changes, renames, deletes, generated files, migrations, lockfiles, and config changes. For PRs, identify the target branch or merge base, and confirm the base ref resolves and the diff is non-empty. A bad ref or empty diff fails here, not mid-review. For local-only reviews, state whether unstaged and untracked files are in scope.
   - If intent is missing, infer it and label it as an assumption, not a fact. When code appears to implement the wrong behavior, check intent against existing system and business logic before reviewing mechanics.
   - If tooling is unavailable because there is no PR platform, the checkout is detached or shallow, or commands fail, degrade gracefully: review what you can access, state which context you could not gather, and treat that gap as residual risk rather than guessing.

2. Read enough context, then stop.
   - Inspect changed files, related tests, called functions, imported modules, neighboring code, and contract-defining files as needed.
   - Identify public surfaces touched: APIs, CLI flags, config, schemas, migrations, events, persisted data, permissions, external integrations, and serialized formats.
   - For generated or mechanical diffs, inspect the generator, source rule, or representative output instead of line-reviewing noise.
   - Bound the reading to the change's blast radius: the changed code and what it directly affects or depends on. Stop expanding once you can defend each finding's evidence; do not read the whole repository to chase hypothetical risk.

3. Scan by risk, not file order.
   - Map every changed file and touched public surface to at least one risk category below, or explicitly clear it, before deciding which findings are worth reporting.
   - Intent fit: logical, system-aligned behavior without scope drift or missing cases.
   - Functional correctness: boundaries, edge cases, missing branches, null/error handling, off-by-one errors, state transitions, concurrency, race conditions, lock ordering, idempotency, and resource lifecycle.
   - Breaking changes: backward and forward compatibility, mixed-version behavior, migrations, defaults, rollback, and external integrations.
   - Developer workflow: changes that break how developers run or build locally — secrets sourced differently, environment variables renamed or newly required, ports remapped, new mandatory setup steps. New alternative paths and ordinary dependency additions do not count.
   - Security and privacy: authorization, input validation, injection, secrets, sensitive logging, personal data, dependency risk, least privilege, and feature-gate leaks — gated or internal-only behavior reachable outside its flag, which is often subtle.
   - Data integrity: old data, partial writes, transaction boundaries, retries, duplicate delivery, and failure recovery.
   - Performance and reliability: N+1 calls, data volume, complexity, batching, caching, timeouts, retries, rate limits, backpressure, observability, and cleanup.
   - Maintainability: scope drift, thin abstractions and pass-through wrappers that add indirection without buying clarity, duplicated logic, unclear boundaries, hidden side effects, contracts muddied by casts or loosely typed escape hatches, naming that obscures intent, large unfocused functions, and code that is hard to test or change safely.

4. Deepen scrutiny where the touched surface requires it.
   - Apply these overlays only when the Step 3 scan or the changed surface calls for them.
   - AI / agent systems (prompts, tool calls, model-visible context, memory, retrieval, agent state, delegation, evals, generated output handling): read `references/ai-agent-systems.md`.
   - Contract surfaces (APIs, config, CLI flags, schemas, migrations, events, persisted records, serialized formats, SDKs, public types, external integration behavior): read `references/contract-surfaces.md`.
   - Frontend / UI (rendered UI, user interaction, forms, navigation, client state, accessibility, responsive layout, browser behavior): read `references/frontend-ui.md`.
   - Trust boundaries (authorization, authentication, secrets, personal data, input validation, dependencies, permissions, network boundaries, uploads, webhooks, privileged operations): read `references/trust-boundaries.md`.
   - Production operations (reliability, background jobs, queues, schedulers, external services, retries, timeouts, migrations, observability, incident response, high-volume paths): read `references/production-operations.md`.

5. Review tests deliberately.
   - Check whether changed behavior has meaningful tests at the right level. Prefer behavior-level and integration coverage for cross-module behavior, workflows, external contracts, and agent logic.
   - Treat missing tests as findings only when tied to concrete behavior risk.
   - Look for false confidence: brittle mocks, assertions that cannot fail, missing edge cases, nondeterminism, fixtures that hide the bug, or tests overfit to implementation.
   - Run focused tests when feasible. If tests are not run, state the gap.
   - Before reporting a suspected bug, try to disprove it: trace the actual call sites, check the boundary or input that would trigger it, and confirm no guard, caller, or existing test already prevents it. If you cannot construct a concrete failing case, downgrade the finding or report it as an assumption rather than a proven defect.

6. Control review size.
   - Flag large non-mechanical diffs as reviewability findings when they are too broad to inspect reliably.
   - Treat a non-mechanical change as too large when you can no longer hold its behavior and dependencies in context well enough to defend each finding. Logic-dense or high-risk changes hit that limit sooner than mechanical ones; calibrate to the repo's norms rather than a fixed line count.
   - Treat reviewability as a finding when change structure blocks reliable review: unrelated changes bundled together, mechanical and semantic edits mixed without separation, generated output without the source rule or generator change, migrations mixed with behavior changes, or broad rewrites without a clear dependency chain.
   - Do not use reviewability as an escape hatch before sampling enough of the diff, touched contracts, and representative call paths to explain why the change cannot be reviewed reliably as submitted.
   - Suggest the smallest coherent stage based on real dependencies, affected call sites, and migration order — for example schema, then core logic, then wiring, then UI, then tests.

7. Convert observations into findings.
   - Report findings as one batch: complete the read-only scan (Steps 1–6) across the whole review surface before presenting any finding, then deliver the full set in a single report. Findings accumulate during the scan; stop mid-scan only when the review premise is invalid — wrong branch or target, unusable scope — or continuing would be unsafe, such as exposed live credentials needing immediate action.
   - Merge findings that share a root cause into one finding listing every affected location.
   - Give each finding a short id (`F1`, `F2`, ...) so later discussion and triage can reference it, and state confidence (high/med/low) alongside severity.
   - Calibrate severity by impact, likelihood, and confidence. Do not escalate severe but unproven risk without evidence; report it at a lower severity with the assumption or uncertainty stated.
   - `Critical`: exploitable security issue, data loss or corruption, system-breaking regression, broken public contract, or complete logic failure.
   - `High`: likely user-visible bug, severe regression, broken migration or rollback path, major performance issue, or explicit project-rule violation.
   - `Medium`: contained but real bug, missing validation, meaningful test gap, brittle logic likely to cause future defects, or maintainability issue with practical risk.
   - `Low`: minor cleanup with practical value; omit unless the user asks for exhaustive review.
   - If there are no findings, say so directly; do not invent low-value findings to avoid an empty review.
   - **Do not report:** guessed intent without concrete evidence; broad rewrites when a local fix addresses the issue; breakage that is the change's stated, scope-constrained intent (a removed flag, a deleted feature) unless its impacts look under-weighed; or issues the repo's linter, formatter, or type-checker already catches. The `Bad findings` examples below show the other shapes to reject.

8. Self-check before finalizing.
   - Confirm every finding meets the `Finding quality` checklist below; drop any that do not, and apply the severity-calibration rule from Step 7 to anything uncertain.
   - Remove findings that would require the author to "check" something the reviewer can inspect, unless the next step is a specific test or measurement that cannot be run in the current environment.

## Output format

Start with findings ordered by severity. Keep scope concise and place it after findings unless the user explicitly asks for a different format. If there are no findings, start with `No findings in the reviewed scope.`

For small reviews (a narrow diff with one or few findings), `Findings`, `Scope`, and `Tests / checks` are sufficient; omit the other sections unless they carry real information. Always include `Tests / checks`; include `Residual risks` when checks were not run or context was unavailable.

Use this structure:

```markdown
## Findings (required; if none, replace this section with "No findings in the reviewed scope.")

### <id> [<severity>/<confidence>] <short title> — path/to/file.ext:42

- **Problem:** <the concrete issue>
- **Evidence:** <specific code path, failing case, example input, violated contract, or reasoning chain>
- **Why it matters:** <behavioral, user, security, operational, or maintainability impact>
- **Proposed fix:** <specific next step>

## Scope (required; place after findings)

<what was reviewed; what is out of scope; stated or inferred intent in one short paragraph>

## Tests / checks (required)

- <tests reviewed or run, and the result; state "not run" with the reason when applicable>

## Open questions / assumptions (optional)

- <inferred intent labeled as assumption, ambiguities to confirm>

## Residual risks (optional; only for material gaps that affect review confidence)

- <material uncertainty from unavailable context, unavailable tooling, or checks that were not run>

## Next steps (optional)

- <smallest actionable review follow-ups for the code author>
```

## Finding quality

Before reporting a finding, check that it has:

- a precise location;
- a concrete trigger condition, failing case, violated contract, or evidence path;
- a real behavior, security, operational, data-integrity, or maintainability impact;
- a severity that matches impact, likelihood, and confidence;
- a specific fix or next step.

Write each finding for a reader who may not have written or even read the code: open with the context needed to situate it — what the code is responsible for, in a line — then state the wrong behavior in one plain sentence before the mechanism, and let the evidence trace the path from trigger to wrong outcome so the reader follows it instead of re-deriving it. When the defect survives because the code invites a natural-but-wrong reading, name that reading and correct it — dislodging the wrong model beats stating the fact beside it. When the mechanism is too tangled to hold in prose — ordering, concurrency, state transitions — shrink the failing case to a minimal toy world (two writers, a three-slot queue) or draw a small mermaid diagram; never illustrate what a sentence covers.

Review in the language and conventions present in the diff. The example below illustrates the shape of a strong finding, not its domain.

Good finding:

> **F1 [High/high] Pagination drops the partial last page** - `src/lib/paginate.ts:24`
> **Problem:** `const pageCount = Math.floor(total / pageSize)` undercounts pages when there is a remainder. With `total = 101` and `pageSize = 25`, it yields `4`, but the caller loops `page < pageCount`, pages `0..3`, so the final item is never returned.
> **Evidence:** The remainder case `total = 101`, `pageSize = 25` needs five pages, `0..4`, but `Math.floor(101 / 25)` produces `4`.
> **Why it matters:** Consumers silently lose the final partial page, breaking the documented "returns all items" contract.
> **Proposed fix:** Use `Math.ceil(total / pageSize)` and add a boundary test for the remainder case.

Bad findings:

- "Consider adding more tests here." - vague, with no behavior risk.
- "This function is a bit long; you might refactor it." - preference with no concrete risk.
- "Ensure this handles errors correctly." - a "verify" chore the reviewer can check directly.
- "Nice clean implementation!" - praise, not a finding.
- "Line 12 sets `count = 0`." - restates the code without identifying an issue.
