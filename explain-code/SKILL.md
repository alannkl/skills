---
name: explain-code
description: Explain existing code at any requested scope, including a change, module, flow, or whole codebase. Use when the user wants to understand what code does, how behavior flows, or what changed. Explanation only; not for code review, diagnosis, implementation, or documentation edits.
---

# Explain Code

Explain what code observably does at the requested scope, whether a change before merge, a function, a subsystem, an end-to-end flow, the whole system, or another slice. The explainer is the deliverable. Optional follow-ups include Q&A on what remains unclear, a quiz to uncover misunderstandings rather than certify mastery, and a micro-world, a small interactive simulation for logic that prose and diagrams cannot convey.

## Boundaries

- Explain only. Never judge code quality, never edit the project's code or comments, never run the project's code. A micro-world (step 8) is a separate throwaway simulation, not an exception.
- If something looks buggy or suspicious while reading, note the observation in one line and suggest a code review; do not develop it into review findings.
- If confusion stems from unclear code rather than from the target itself, say so and suggest a documentation or simplification pass; do not fix the code here.
- If the user wants proof the code works, suggest runtime verification; this skill checks the user's understanding, not the code's correctness.

## Workflow

1. Resolve the requested scope. Any slice of code is valid. State the resolved scope in one line at the top of the explainer so a misread surfaces immediately.
   - **Change**: a diff. Default to the current branch plus working tree against its merge base with the default branch; accept an explicit commit range, PR, staged changes, or file set. The diff is the ground truth. If it is empty, report that there is nothing to explain and stop.
   - **Part**: a named function, class, module, feature, subsystem, directory, or file set. Resolve which files or regions implement it by reading, not guessing; if the name maps to several plausible units, name the mapping you chose.
   - **System**: the whole codebase or a whole service.
   - **Anything else**: an end-to-end flow, a cross-cutting concern (error handling, authentication), a scenario ("what happens on login"). Resolve it to the implementing code and borrow the nearest anchor's guidance.
   - When the request is ambiguous ("explain this"), infer from context — a just-completed change means change scope, an open or named file means part scope — and say what you resolved.

2. Gather enrichment, but never depend on it.
   - For change scope, use the implementing session's context and any implementation-notes file the project keeps as sources for rationale. For part and system scope, use READMEs, ADRs, and design docs.
   - Look for recorded rationale in repository history, including commit messages, blame, and PR descriptions.
   - Work from the repository alone when session context is unavailable. When rationale is unrecorded, infer it from the code and label the inference. If the code gives no basis for one, say the rationale is not recorded. Present-day coherence does not establish original intent, and original reasons may no longer apply.

3. Understand behavior at the requested scope. Read enough surrounding code, including callers, tests, configuration, and error paths, to describe outputs, side effects, timing, failure modes, and user-visible results. A list of functions or files is insufficient. Stop reading when you can explain every step from input to output or trigger to effect.
   - Change: what the system did before and does now, per behavior.
   - Part: what the unit is responsible for, its inputs and outputs, its key flows and failure modes, and how the rest of the system uses it.
   - System: what the system does for its users, the major components and their responsibilities, the key end-to-end flows, and where important state lives. Stay at architecture altitude; per-function detail belongs in part scope.
   - Other scopes: adapt the nearest scope's level of detail. For example, explain a login flow as a part traced across components.

4. Present the explainer in chat. Do not write it to a file. Order it for comprehension:
   - Infer the user's purpose from the conversation, without quizzing them, and focus detail on their question. Editing, reviewing, debugging, and learning unfamiliar code call for different explanations. When no purpose is apparent, write for the engineer who will maintain the code.
   - Open with the surrounding-system context needed to follow the explanation, scaled to what the user already knows. The author of a fresh change may need a sentence; a newcomer needs more.
   - Before code-level detail, state the essence in a few sentences and walk through one concrete input and its observable result. If the real system is too large for a clear example, use a minimal imaginary one, such as two nodes or a three-slot queue. Keep only what makes the mechanism visible. This is a prose thought experiment; the interactive micro-world is in step 8.
   - Add a contrasting example, such as an edge case or another branch, only when the boundary between behaviors is the hard part. If the code invites a plausible misreading, name and correct it. If it implements a known pattern, such as a ring buffer, debouncing, or two-phase commit, name the pattern naturally and tie it to this case.
   - Then the details: follow the flow of behavior with a line of prose introducing each part, not a file-by-file listing.
   - Change scope covers each behavior before and after the change, why it changed, and what to watch for after merge. Explain the invariant future edits must preserve and an edit that would break it. Ground the rationale in session context or notes when available; otherwise label it as inference.
   - Part scope covers the unit's responsibility, key behaviors and flows, edge cases and failure modes, and how it interacts with the rest of the system. Include what the unit assumes about that system.
   - System scope covers: what the system does, the major components and how they collaborate, the key end-to-end flows, and the load-bearing design decisions a newcomer must know.
   - Other scopes: adapt the nearest scope's coverage to what the user needs to understand the requested slice.
   - If the user will edit, review, or debug the source next, close with only the files needed to start and a reason to open each. For example, pair a handler with the worker that consumes its rows. For every other purpose, omit file listings.
   - State the explanation directly. Omit framing labels such as "the key insight", "at its core", or "TL;DR", and announcements such as "here's the tricky part" or "this is where it gets interesting".
   - Use a sequence, state, flow, or component diagram when it explains more clearly than prose, such as for control flow across components, state transitions, ordering, or branching failure paths. Write diagrams in mermaid. Use prose alone when a sentence suffices. For anything with three or more moving parts, draw a short series in which each diagram redraws the last and adds one part.
   - Write for the user and keep the explainer self-contained enough to reuse verbatim as a PR description for change scope or an onboarding or architecture note otherwise.
   - Offer all follow-ups together: Q&A in step 5, a durable home in step 6, the quiz in step 7, and a micro-world only when step 8 warrants one. Use one numbered list with consecutive numbers for the options offered. Invite replies by number alone, such as "1", "2 3", or "all".
   - Then stop and let the user read. Run only what the user accepts, in step order when several are picked; when the session winds down, restate any offers from this list the user has not yet answered.

5. Run a Q&A session when the user opts in: answer follow-up questions about the explained code until the user is satisfied. On acceptance, read `references/qa.md` and follow it.

6. Give the explainer a durable home when the user opts in: write it where future readers will already look. On acceptance, read `references/durable-home.md` and follow it.

7. Quiz the user when they opt in: one round of multiple-choice questions on missable behavior, then score and re-teach. On acceptance, read `references/quiz.md` and follow it.

8. Build a micro-world when warranted and opted into: a tiny interactive simulation the user inhabits to feel the logic work. On acceptance, read `references/micro-world.md` and follow it.
   - Warranted only for logic that is hard to hold by reading — state machines, coordinate or geometry math, multi-step transformations, scheduling or concurrency, algorithmic edge cases. If the logic reads fine, skip it entirely and do not offer one; prose, examples, and mermaid come first.
