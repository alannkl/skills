---
name: explain-code
description: Explain code at any requested scope — a change, a module, a flow, or the whole codebase — with an optional quiz that surfaces understanding gaps and an optional interactive micro-world for hard-to-hold logic.
disable-model-invocation: true
---

# Explain Code

Help the user genuinely understand code at the scope they request — a change before merge, a function, a subsystem, an end-to-end flow, the whole system, or any other slice. Present an explainer of what that code observably does; the explainer is the deliverable. Two optional mechanisms sit on top: a quiz — a misunderstanding detector, not a mastery gate — that surfaces missing or wrong understanding fast and cheaply, and a micro-world — a small interactive simulation for logic that prose and diagrams cannot make felt.

## Boundaries

- Explain only. Never judge code quality, never edit the project's code or comments, never run the project's code. A micro-world (step 5) is a separate throwaway simulation, not an exception.
- If something looks buggy or suspicious while reading, note the observation in one line and suggest a code review; do not develop it into review findings.
- If confusion stems from unclear code rather than from the target itself, say so and suggest a documentation or simplification pass; do not fix the code here.
- If the user wants proof the code works, suggest runtime verification; this skill checks the user's understanding, not the code's correctness.

## Workflow

1. Resolve the requested scope. Any slice of code is valid; the shapes below are common anchors, not a closed list. State the resolved scope in one line at the top of the explainer so a misread surfaces immediately.
   - **Change**: a diff. Default to the current branch plus working tree against its merge base with the default branch; accept an explicit commit range, PR, staged changes, or file set. The diff is the ground truth. If it is empty, report that there is nothing to explain and stop.
   - **Part**: a named function, class, module, feature, subsystem, directory, or file set. Resolve which files or regions implement it by reading, not guessing; if the name maps to several plausible units, name the mapping you chose.
   - **System**: the whole codebase or a whole service.
   - **Anything else** — an end-to-end flow, a cross-cutting concern (error handling, authentication), a scenario ("what happens on login"). Resolve it to the implementing code and borrow the nearest anchor's guidance.
   - When the request is ambiguous ("explain this"), infer from context — a just-completed change means change scope, an open or named file means part scope — and say what you resolved.

2. Gather enrichment, but never depend on it.
   - For change scope, use the implementing session's context and any implementation-notes file the project keeps as sources for rationale. For part and system scope, use READMEs, ADRs, and design docs.
   - The skill must work in a fresh session with nothing but the repository. When rationale is unrecorded, infer it from the code and label it as inference; when the code offers no basis to infer, say the rationale is not recorded.

3. Understand the behavior at the target's altitude. Read enough surrounding code — callers, tests, configuration, error paths — to describe observable behavior: outputs, side effects, timing, failure modes, user-visible results. Not which functions or files exist.
   - Change: what the system did before and does now, per behavior.
   - Part: what the unit is responsible for, its inputs and outputs, its key flows and failure modes, and how the rest of the system uses it.
   - System: what the system does for its users, the major components and their responsibilities, the key end-to-end flows, and where important state lives. Stay at architecture altitude; per-function detail belongs in part scope.
   - Other scopes: pick the altitude that matches the scope's size and interpolate — a login flow reads like a part traced across components, not a system overview.

4. Present the explainer in chat. Do not write it to a file. Order it teach-first:
   - Background first: the surrounding-system context needed to follow the rest, scaled to what the user already knows — the author of a fresh change needs a sentence; a newcomer needs more. Never open with the details.
   - Intuition before details: state the essence in a few sentences and walk one concrete example — a real or toy input and its observable result — before any code-level detail.
   - Then the details, ordered for comprehension: follow the flow of behavior with a line of prose introducing each part, not a file-by-file listing.
   - Change scope covers: what the system now does differently (before → after, per behavior), why (from session context or notes when available, labeled inference otherwise), and what to watch for after merge.
   - Part scope covers: the unit's responsibility, its key behaviors and flows, its edge cases and failure modes, and how it interacts with the rest of the system.
   - System scope covers: what the system does, the major components and how they collaborate, the key end-to-end flows, and the load-bearing design decisions a newcomer must know.
   - Other scopes: cover what the user needs to hold the slice in their head — adapt the nearest anchor's coverage rather than forcing the slice into it.
   - Use a diagram (sequence, state, flow, component) whenever it beats prose — control flow across components, state transitions, ordering, branching failure paths. Write diagrams in mermaid; the source reads fine in chat and renders wherever the explainer is reused. Never diagram what a sentence covers.
   - Write it for the user, but keep it self-contained enough to reuse verbatim — as a PR description for change scope, as an onboarding or architecture note otherwise.
   - Stop after presenting it and let the user read. Make all offers now, in one short line — the durable home for the explainer (step 8), the quiz, and a micro-world when step 5 warrants one — so nothing is lost if the user leaves after reading. Run each only on request or acceptance.

5. Build a micro-world when warranted and opted into: a tiny interactive simulation the user inhabits to feel the logic work.
   - Warranted only for logic that is hard to hold by reading — state machines, coordinate or geometry math, multi-step transformations, scheduling or concurrency, algorithmic edge cases. If the logic reads fine, skip it entirely and do not offer one; prose, examples, and mermaid come first.
   - Build a single self-contained HTML file — embedded CSS and JavaScript, no external dependencies — that simulates just the target logic with example data and lets the user probe it: scrub steps, drag inputs, toggle branches, watch the result change.
   - Derive the simulated logic directly from the source and name every simplification. It models the code — it is not the code, and passing in the simulation proves nothing about runtime.
   - Every control must answer a "what happens if" question the user could actually ask; interactivity that only decorates teaches nothing — fall back to a static diagram.
   - Write it to a scratch or temp location, or publish it as an artifact where the harness supports that — never into the project tree.

6. Quiz the user when they opt in, one round.
   - Ask multiple-choice questions about what the target code observably does — "what happens when X?" is the typical shape, not a required template.
   - Quiz only non-obvious, easy-to-miss behavior: edge cases, failure paths, defaults, interactions between components or changes. Hard because the behavior is easy to miss, never because the question is tricky or hinges on incidental details. Skip anything already obvious from the explainer's summary or the user's own request — a question answerable without thinking detects nothing.
   - No quota: ask the minimum that covers the genuinely missable behaviors — often just two or three questions. If the target offers none, say so and skip the quiz; never pad the round with easy questions.
   - Every option must be a plausible behavior. No giveaway options, no symbol trivia (never "which function/file/pattern"), and for change scope no questions about unchanged behavior.
   - Shuffle the correct option's position from question to question, and keep all options similar in length and detail; a fixed slot or a longest-option-wins pattern is a tell.
   - Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages. Confirm right or wrong in one line after each answer; save re-teaching for the end of the round.

7. Score and re-teach.
   - After the round, report the score and each misunderstanding surfaced.
   - For each miss, re-explain the behavior with a pointer into the explainer or the code.
   - Do not force a re-quiz. If the score was low, end with a concrete suggestion: re-read the named explainer sections or code, then re-run the skill.

8. Close, whether or not a quiz ran. The explainer is too valuable to strand in chat — if the durable-home offer from step 4 is still unanswered, restate it; write only on acceptance.
   - Change scope: offer the explainer text as the PR description or extended commit-message body, so it persists where reviewers and future readers already look.
   - Other scopes: name the concrete destination where the explainer belongs — the relevant README section, an existing docs page, an architecture note — not a vague "this could be documented". Keep it markdown; mermaid renders where docs live.
   - Never update docs or run git or gh commands unasked: an explainer is written for one reader at one moment; silently merging it into shared docs invites rot and duplication. On acceptance, adapt it to the destination's audience rather than pasting verbatim.

## Gotchas

- A quiz the user can pattern-match without understanding is worse than no quiz: it certifies a gap as covered.
- The quiz's value is entirely in its hardest questions. Three questions on genuinely missable behavior beat seven that re-ask the explainer.
- Do not pad the explainer with restated diff hunks or file-by-file inventories; it explains behavior and structure, not the patch or the directory tree.
- Depth must scale inversely with scope: a system explainer that walks every directory is an inventory, not an explanation. Widen the altitude, don't multiply the words.
- Inferred rationale presented as fact misleads; write "rationale not recorded" rather than stretching an inference the code cannot support.
- A micro-world drifts from the source easily: rebuild it after the code changes rather than trusting an old simulation, and never let its behavior stand in for what the code does.
