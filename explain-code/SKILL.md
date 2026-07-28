---
name: explain-code
description: Explain code at any scope the user requests — a completed change, a single function, a module or feature, an end-to-end flow, or the whole codebase — with an optional lightweight quiz that surfaces gaps in the user's understanding. Use when the user asks to explain this change, walk me through what changed, explain this module or function, how does X work, give a codebase or architecture overview, or quiz me on it. Do not use for judging code quality, adding comments or docs, refactoring, or verifying that the code works at runtime.
---

# Explain Code

Help the user genuinely understand code at the scope they request — a change before merge, a single function, a part of the codebase, an end-to-end flow, the whole system, or any other slice. Present an explainer of what that code observably does; that explainer is the deliverable. The quiz is an optional mechanism on top — a misunderstanding detector, not a mastery gate: its only job is to surface missing or wrong understanding fast and cheaply.

## Boundaries

- Explain only. Never judge code quality, never edit code or comments, never run the code.
- If something looks buggy or suspicious while reading, note the observation in one line and suggest a code review; do not develop it into review findings.
- If confusion stems from unclear code rather than from the target itself, say so and suggest a documentation or simplification pass; do not fix the code here.
- If the user wants proof the code works, suggest runtime verification; this skill checks the user's understanding, not the code's correctness.

## Workflow

1. Resolve the requested scope. Any slice of code is valid; the shapes below are common anchors, not a closed list. State the resolved scope in one line at the top of the explainer so a misread surfaces immediately.
   - **Change**: a diff. Default to the current branch plus working tree against its merge base with the default branch; accept an explicit commit range, PR, staged changes, or file set. The diff is the ground truth. If the resolved diff is empty, report that there is nothing to explain and stop.
   - **Part**: a named function, class, module, feature, subsystem, directory, or file set. Resolve which files or regions implement it by reading, not guessing; if the name maps to several plausible units, name the mapping you chose.
   - **System**: the whole codebase or a whole service.
   - **Anything else** — an end-to-end flow, a cross-cutting concern (error handling, authentication), a scenario ("what happens on login"). Resolve it to the code that implements it and borrow the nearest anchor's guidance.
   - When the request is ambiguous ("explain this"), infer from context — a just-completed change means change scope, an open or named file means part scope — and say what you resolved.

2. Gather enrichment, but never depend on it.
   - For change scope, use the implementing session's context and any implementation-notes file the project keeps as sources for rationale. For part and system scope, use READMEs, ADRs, and design docs the repository keeps.
   - The skill must work in a fresh session with nothing but the repository. When rationale or intent is unrecorded, infer it from the code and label it clearly as inference; when the code offers no basis to infer, say the rationale is not recorded.

3. Understand the behavior at the target's altitude. Read enough surrounding code — callers, tests, configuration, error paths — to describe observable behavior: outputs, side effects, timing, failure modes, user-visible results. Not which functions or files exist.
   - Change: what the system did before and does now, per behavior.
   - Part: what the unit is responsible for, its inputs and outputs, its key flows and failure modes, and how the rest of the system uses it.
   - System: what the system does for its users, the major components and their responsibilities, the key end-to-end flows, and where important state lives. Stay at architecture altitude; per-function detail belongs in part scope.
   - Other scopes: pick the altitude that matches the scope's size and interpolate between the anchors — a login flow reads like a part traced across components, not like a system overview.

4. Present the explainer in chat. Do not write it to a file.
   - Change scope covers: what the system now does differently (before → after, per behavior), why (from session context or notes when available, clearly labeled inference otherwise), and what to watch for after merge.
   - Part scope covers: the unit's responsibility, its key behaviors and flows, its edge cases and failure modes, and how it interacts with the rest of the system.
   - System scope covers: what the system does, the major components and how they collaborate, the key end-to-end flows, and the load-bearing design decisions a newcomer must know.
   - Other scopes: cover what the user would need to hold the slice in their head — adapt the nearest anchor's coverage rather than forcing the slice into it.
   - Use a diagram (sequence, state, flow, component) whenever it conveys structure or behavior better than prose — multi-component control flow, state transitions, ordering, branching failure paths, component relationships. Write diagrams in mermaid; the source reads fine in chat and renders wherever the explainer is reused. Never diagram what a sentence covers.
   - Write it for the user, but keep it self-contained enough to reuse verbatim — as a PR description for change scope, as an onboarding or architecture note otherwise.
   - Stop after presenting it and let the user read. Offer the quiz; run it only when the user asked for one (for example "quiz me") or accepts the offer.

5. Quiz the user when they opt in, one round.
   - Ask multiple-choice questions about what the target code observably does — "what happens when X?" is the typical shape, not a required template.
   - Quiz only non-obvious, easy-to-miss behavior: edge cases, failure paths, defaults, interactions between components or changes. Skip anything the explainer's summary or the user's own request already makes obvious — a question the user can answer without thinking detects nothing.
   - No quota: ask the minimum that covers the genuinely missable behaviors — often just two or three questions. If the target offers no such questions, say so and skip the quiz; never pad the round with easy questions.
   - Every option must be a plausible behavior. No giveaway options, no symbol trivia (never "which function/file/pattern"), and for change scope no questions about unchanged behavior.
   - Shuffle the correct option's position from question to question; a fixed slot is a tell.
   - Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages.

6. Score and re-teach.
   - After the round, report the score and each misunderstanding surfaced.
   - For each miss, re-explain the behavior with a pointer into the explainer or the code.
   - Do not force a re-quiz. If the score was low, end with a concrete suggestion: re-read the named explainer sections or code, then re-run the skill.

7. Close, whether or not a quiz ran.
   - Change scope: offer the explainer text as the PR description or extended commit-message body, so it persists where reviewers and future readers already look.
   - Other scopes: note that the explainer can seed project documentation if the user wants to keep it.
   - Suggest the text only; do not run git or gh commands, and do not write documentation files, unless asked.

## Gotchas

- A quiz the user can pattern-match without understanding is worse than no quiz: it certifies a gap as covered.
- The quiz's value is entirely in its hardest questions. Three questions on genuinely missable behavior beat seven that re-ask the explainer.
- Do not pad the explainer with restated diff hunks or file-by-file inventories; it explains behavior and structure, not the patch or the directory tree.
- Depth must scale inversely with scope: a system explainer that walks every directory is an inventory, not an explanation. Widen the altitude, don't multiply the words.
- Inferred rationale or intent presented as fact misleads; write "rationale not recorded" rather than stretching an inference the code cannot support.
