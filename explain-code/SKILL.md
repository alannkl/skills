---
name: explain-code
description: Explain code at any requested scope — a change, a module, a flow, or the whole codebase — with optional follow-up Q&A, a quiz that surfaces understanding gaps, and an interactive micro-world for hard-to-hold logic.
disable-model-invocation: true
---

# Explain Code

Help the user genuinely understand code at the scope they request — a change before merge, a function, a subsystem, an end-to-end flow, the whole system, or any other slice. Present an explainer of what that code observably does; the explainer is the deliverable. Three optional mechanisms sit on top: a Q&A session for what the explainer left open, a quiz — a misunderstanding detector, not a mastery gate — that surfaces missing or wrong understanding fast and cheaply, and a micro-world — a small interactive simulation for logic that prose and diagrams cannot make felt.

## Boundaries

- Explain only. Never judge code quality, never edit the project's code or comments, never run the project's code. A micro-world (step 9) is a separate throwaway simulation, not an exception.
- If something looks buggy or suspicious while reading, note the observation in one line and suggest a code review; do not develop it into review findings.
- If confusion stems from unclear code rather than from the target itself, say so and suggest a documentation or simplification pass; do not fix the code here.
- If the user wants proof the code works, suggest runtime verification; this skill checks the user's understanding, not the code's correctness.

## Workflow

1. Resolve the requested scope. Any slice of code is valid; the shapes below are common anchors, not a closed list. State the resolved scope in one line at the top of the explainer so a misread surfaces immediately.
   - **Change**: a diff. Default to the current branch plus working tree against its merge base with the default branch; accept an explicit commit range, PR, staged changes, or file set. The diff is the ground truth. If it is empty, report that there is nothing to explain and stop.
   - **Part**: a named function, class, module, feature, subsystem, directory, or file set. Resolve which files or regions implement it by reading, not guessing; if the name maps to several plausible units, name the mapping you chose.
   - **System**: the whole codebase or a whole service.
   - **Anything else**: an end-to-end flow, a cross-cutting concern (error handling, authentication), a scenario ("what happens on login"). Resolve it to the implementing code and borrow the nearest anchor's guidance.
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
   - Make every offer at once, so nothing is lost if the user leaves after reading: a Q&A session on the explainer (step 5), a durable home for the explainer (step 6), the quiz (step 7), and — only when step 9 warrants one — a micro-world. Present them as one numbered list — number only the options actually offered, with no gaps — and invite replies by number alone: "1", "2 3", or "all".
   - Then stop and let the user read. Run only what the user accepts, in step order when several are picked.

5. Run a Q&A session when the user opts in: answer follow-up questions about the explained code until the user is satisfied.
   - Ground every answer in the source. Answer from what was already read when it suffices; re-read or widen the reading when the question exceeds it. Distinguish what the code shows, what you infer, and what is not recorded — never fill a gap with a guess.
   - Match the answer's altitude to the question: a "why does X happen" gets the behavior traced through the code, not a restated explainer section.
   - The boundaries above still hold: explain only — a "should this be refactored?" gets a one-line observation and a suggestion to run a code review, not a critique.
   - When a question reveals the explainer skipped something load-bearing, answer it and note the gap; if the user later accepts the durable-home offer, fold that answer in.
   - When the session winds down, restate any offers from step 4 the user has not yet answered.

6. Give the explainer a durable home: write on acceptance, and if the step 4 offer is still unanswered when the session winds down, restate it before closing.
   - Change scope: offer the explainer text as the PR description or extended commit-message body, so it persists where reviewers and future readers already look.
   - Other scopes: name the concrete destination where the explainer belongs — the relevant README section, an existing docs page, an architecture note — not a vague "this could be documented". Keep it markdown; mermaid renders where docs live.
   - Never update docs or run git or gh commands unasked: an explainer is written for one reader at one moment; silently merging it into shared docs invites rot and duplication. On acceptance, adapt it to the destination's audience rather than pasting verbatim.
   - Write the full explanation, not a summary, unless the user asks for less.
   - The final document must read as a single cohesive explanation, not an original plus an appended explainer: where the destination already covers a point the explainer also makes, fold the explainer's treatment into that existing content so nothing is explained twice; content the destination doesn't cover is simply added where it fits the document's flow.
   - Carry the explainer's diagrams over with it, placed where they support the surrounding text — unless the destination already has a diagram covering the same thing, in which case keep the existing one.

7. Quiz the user when they opt in, one round.
   - Ask multiple-choice questions about what the target code observably does — "what happens when X?" is the typical shape, not a required template.
   - Quiz only non-obvious, easy-to-miss behavior: edge cases, failure paths, defaults, interactions between components or changes. Hard because the behavior is easy to miss, never because the question is tricky or hinges on incidental details. Skip anything already obvious from the explainer's summary or the user's own request — a question answerable without thinking detects nothing.
   - No quota: ask the minimum that covers the genuinely missable behaviors — often just two or three questions. If the target offers none, say so and skip the quiz; never pad the round with easy questions.
   - Every option must be a plausible behavior. No symbol trivia (never "which function/file/pattern"), and for change scope no questions about unchanged behavior.
   - Shuffle the correct option's position from question to question, and keep all options similar in length and detail; a fixed slot or a longest-option-wins pattern is a tell.
   - Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages. Confirm right or wrong in one line after each answer; save re-teaching for the end of the round.

8. Score and re-teach.
   - After the round, report the score and each misunderstanding surfaced.
   - For each miss, re-explain the behavior with a pointer into the explainer or the code.
   - Do not force a re-quiz. If the score was low, end with a concrete suggestion: re-read the named explainer sections or code, then re-run the skill.

9. Build a micro-world when warranted and opted into: a tiny interactive simulation the user inhabits to feel the logic work.
   - Warranted only for logic that is hard to hold by reading — state machines, coordinate or geometry math, multi-step transformations, scheduling or concurrency, algorithmic edge cases. If the logic reads fine, skip it entirely and do not offer one; prose, examples, and mermaid come first.
   - Build a single self-contained HTML file — embedded CSS and JavaScript, no external dependencies — that simulates just the target logic with example data and lets the user probe it: scrub steps, drag inputs, toggle branches, watch the result change.
   - Derive the simulated logic directly from the source and name every simplification. It models the code — it is not the code, and passing in the simulation proves nothing about runtime.
   - Every control must answer a "what happens if" question the user could actually ask; interactivity that only decorates teaches nothing — fall back to a static diagram.
   - Write it to a `.tmp/` folder under the repo root (creating the folder if needed), or publish it as an artifact where the harness supports that. It is throwaway: never commit it and never write it anywhere else in the project tree.

## Gotchas

- A quiz the user can pattern-match without understanding is worse than no quiz: it certifies a gap as covered.
- The quiz's value is entirely in its hardest questions. Three questions on genuinely missable behavior beat seven that re-ask the explainer.
- Do not pad the explainer with restated diff hunks or file-by-file inventories; it explains behavior and structure, not the patch or the directory tree.
- Depth must scale inversely with scope: a system explainer that walks every directory is an inventory, not an explanation. Widen the altitude, don't multiply the words.
- A micro-world drifts from the source easily: rebuild it after the code changes rather than trusting an old simulation.
