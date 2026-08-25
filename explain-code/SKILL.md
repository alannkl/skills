---
name: explain-code
description: Explain code at any requested scope — a change, a module, a flow, or the whole codebase — with optional follow-up Q&A, a quiz that surfaces understanding gaps, and an interactive micro-world for hard-to-hold logic.
disable-model-invocation: true
---

# Explain Code

Help the user genuinely understand code at the scope they request — a change before merge, a function, a subsystem, an end-to-end flow, the whole system, or any other slice. Present an explainer of what that code observably does; the explainer is the deliverable. Three optional mechanisms sit on top: a Q&A session for what the explainer left open, a quiz — a misunderstanding detector, not a mastery gate — that surfaces missing or wrong understanding fast and cheaply, and a micro-world — a small interactive simulation for logic that prose and diagrams cannot make felt.

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
   - Mine the repository's history for recorded rationale: commit messages, blame, and PR descriptions often hold the why nothing else recorded.
   - The skill must work in a fresh session with nothing but the repository. When rationale is unrecorded, infer it from the code and label it as inference; when the code offers no basis to infer, say the rationale is not recorded. Beware retrofitted intent: code that makes sense today may have been written for reasons that no longer apply, or for no good reason at all — an honest "not recorded" beats a plausible invented story.

3. Understand the behavior at the target's altitude. Read enough surrounding code — callers, tests, configuration, error paths — to describe observable behavior: outputs, side effects, timing, failure modes, user-visible results. Not which functions or files exist. Stop reading when you can describe the full path from input to output (or trigger to effect) without hand-waving any step.
   - Change: what the system did before and does now, per behavior.
   - Part: what the unit is responsible for, its inputs and outputs, its key flows and failure modes, and how the rest of the system uses it.
   - System: what the system does for its users, the major components and their responsibilities, the key end-to-end flows, and where important state lives. Stay at architecture altitude; per-function detail belongs in part scope.
   - Other scopes: pick the altitude that matches the scope's size and interpolate — a login flow reads like a part traced across components, not a system overview.

4. Present the explainer in chat. Do not write it to a file. Order it for comprehension:
   - Depth follows purpose: read why the user is asking — about to change the code, reviewing it, debugging it, new to it — from the conversation, not by quizzing them, and put the depth where their question is. A reviewer, a debugger, and a newcomer need different explainers of the same code.
   - Background first: the surrounding-system context needed to follow the rest, scaled to what the user already knows — the author of a fresh change needs a sentence; a newcomer needs more. Never open with the details.
   - Intuition before details: state the essence in a few sentences and walk one concrete example — a real or toy input and its observable result — before any code-level detail. When the real system is too big to hold even for one example, shrink the world itself into a minimal imaginary one — two nodes, a three-slot queue — keeping only what makes the mechanism visible; this is a prose thought experiment, not the interactive micro-world of step 8. Walk a second, contrasting example — an edge case, the other branch — only when the boundary between behaviors is the hard part; a happy path alone hides it. When the code invites a natural-but-wrong reading, name that reading and correct it; dislodging the wrong model beats stating the right one beside it. When the code implements a known named pattern — a ring buffer, debouncing, two-phase commit — say the name the way a senior engineer would say it out loud, then tie it to this case; a recognized name is the cheapest intuition there is.
   - Then the details: follow the flow of behavior with a line of prose introducing each part, not a file-by-file listing.
   - Change scope covers: what the system now does differently (before → after, per behavior), why (from session context or notes when available, labeled inference otherwise), and what to watch for after merge.
   - Part scope covers: the unit's responsibility, its key behaviors and flows, its edge cases and failure modes, and how it interacts with the rest of the system.
   - System scope covers: what the system does, the major components and how they collaborate, the key end-to-end flows, and the load-bearing design decisions a newcomer must know.
   - Other scopes: cover what the user needs to hold the slice in their head — adapt the nearest anchor's coverage rather than forcing the slice into it.
   - When the user's purpose is to edit the code next, close with a minimal where-things-live map — only the files needed to start working; for every other purpose, keep file listings out entirely.
   - Say things directly: no framing labels ("the key insight", "at its core", "TL;DR") and no pacing theater ("here's the tricky part", "this is where it gets interesting") — just say it.
   - Use a diagram (sequence, state, flow, component) whenever it beats prose — control flow across components, state transitions, ordering, branching failure paths. Write diagrams in mermaid; the source reads fine in chat and renders wherever the explainer is reused. Never diagram what a sentence covers. For anything with three or more moving parts, draw a short series where each diagram redraws the last and adds one part, so the reader watches the system assemble — three small growing diagrams beat one crowded diagram.
   - Write it for the user, but keep it self-contained enough to reuse verbatim — as a PR description for change scope, as an onboarding or architecture note otherwise.
   - Make every offer at once, so nothing is lost if the user leaves after reading: a Q&A session on the explainer (step 5), a durable home for the explainer (step 6), the quiz (step 7), and — only when step 8 warrants one — a micro-world. Present them as one numbered list — number only the options actually offered, with no gaps — and invite replies by number alone: "1", "2 3", or "all".
   - Then stop and let the user read. Run only what the user accepts, in step order when several are picked; when the session winds down, restate any offers from this list the user has not yet answered.

5. Run a Q&A session when the user opts in: answer follow-up questions about the explained code until the user is satisfied. On acceptance, read `references/qa.md` and follow it.

6. Give the explainer a durable home when the user opts in: write it where future readers will already look. On acceptance, read `references/durable-home.md` and follow it.

7. Quiz the user when they opt in: one round of multiple-choice questions on missable behavior, then score and re-teach. On acceptance, read `references/quiz.md` and follow it.

8. Build a micro-world when warranted and opted into: a tiny interactive simulation the user inhabits to feel the logic work. On acceptance, read `references/micro-world.md` and follow it.
   - Warranted only for logic that is hard to hold by reading — state machines, coordinate or geometry math, multi-step transformations, scheduling or concurrency, algorithmic edge cases. If the logic reads fine, skip it entirely and do not offer one; prose, examples, and mermaid come first.
