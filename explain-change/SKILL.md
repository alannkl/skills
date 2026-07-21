---
name: explain-change
description: Explain a completed code change before merge, with an optional lightweight quiz that surfaces gaps in the user's understanding of the new behavior. Use when the user asks to explain this change, walk me through what changed, quiz me on it, or wants a pre-merge understanding check. Do not use for judging code quality, adding comments or docs, refactoring, or verifying that the change works at runtime.
---

# Explain Change

Help the owner of a completed change genuinely understand it before merging. Present an explainer of what the system now observably does differently; that explainer is the deliverable. The quiz is an optional mechanism on top — a misunderstanding detector, not a mastery gate: its only job is to surface missing or wrong understanding fast and cheaply.

## Boundaries

- Explain only. Never judge code quality, never edit code or comments, never run the code.
- If something looks buggy or suspicious while reading, note the observation in one line and suggest a code review; do not develop it into review findings.
- If confusion stems from unclear code rather than from the change itself, say so and suggest a documentation or simplification pass; do not fix the code here.
- If the user wants proof the change works, suggest runtime verification; this skill checks the user's understanding, not the code's correctness.

## Workflow

1. Resolve the target diff. The diff is the ground truth.
   - Default to the current branch plus working tree against its merge base with the default branch.
   - Accept an explicit commit range, PR, staged changes, or file set when the user names one.
   - If the resolved diff is empty, report that there is nothing to explain and stop.

2. Gather enrichment, but never depend on it.
   - Use the implementing session's context when this runs in that session, and any implementation-notes file the project keeps, as sources for rationale.
   - The skill must work in a fresh session with nothing but the diff and the repository. When rationale is unrecorded, infer it from the code and label it clearly as inference; when the code offers no basis to infer, say the rationale is not recorded.

3. Understand the behavior change.
   - Read enough surrounding code to know what the system did before and does now: callers, tests, configuration, error paths.
   - Focus on observable behavior — outputs, side effects, timing, failure modes, user-visible results — not on which functions or files changed.

4. Present the explainer in chat. Do not write it to a file.
   - Cover: what the system now does differently (before → after, per behavior), why (from session context or notes when available, clearly labeled inference from the code otherwise), and what to watch for after merge.
   - Use a diagram (sequence, state, flow) whenever it conveys the behavior change better than prose — multi-component control flow, state transitions, ordering, branching failure paths. Write diagrams in mermaid; the source reads fine in chat and renders wherever the explainer is reused. Never diagram what a sentence covers.
   - Write it for the change owner, but keep it self-contained enough to reuse verbatim as a PR description.
   - Stop after presenting it and let the user read. Offer the quiz; run it only when the user asked for one (for example "quiz me") or accepts the offer.

5. Quiz the user when they opt in, one round.
   - Ask multiple-choice questions about what the changed system observably does — "what happens when X?" is the typical shape, not a required template.
   - Quiz only non-obvious, easy-to-miss behavior: edge cases, failure paths, defaults, interactions between changes. Skip anything the explainer's summary or the user's own request already makes obvious — a question the author can answer without thinking detects nothing.
   - No quota: ask the minimum that covers the genuinely missable behaviors — often just two or three questions. If the change offers no such questions, say so and skip the quiz; never pad the round with easy questions.
   - Every option must be a plausible behavior. No giveaway options, no symbol trivia (never "which function/file/pattern"), no questions about unchanged behavior.
   - Shuffle the correct option's position from question to question; a fixed slot is a tell.
   - Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages.

6. Score and re-teach.
   - After the round, report the score and each misunderstanding surfaced.
   - For each miss, re-explain the behavior with a pointer into the explainer or the code.
   - Do not force a re-quiz. If the score was low, end with a concrete suggestion: re-read the named explainer sections or code, then re-run the skill.

7. Close, whether or not a quiz ran.
   - Offer the explainer text as the PR description or extended commit-message body, so it persists where reviewers and future readers already look. Suggest the text only; do not run git or gh commands unless asked.

## Gotchas

- A quiz the user can pattern-match without understanding is worse than no quiz: it certifies a gap as covered.
- The quiz's value is entirely in its hardest questions. Three questions on genuinely missable behavior beat seven that re-ask the explainer.
- Do not pad the explainer with restated diff hunks; it explains behavior, not the patch.
- Inferred rationale presented as fact misleads; write "rationale not recorded" rather than stretching an inference the code cannot support.
