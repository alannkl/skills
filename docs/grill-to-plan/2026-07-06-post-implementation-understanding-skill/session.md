# Post-Implementation Understanding Skill

Date: 2026-07-06
Status: Complete

## Current Understanding

Design (not yet build) the candidate skill from `docs/working-with-agents.md` principle #11: after an agent completes a substantial change, generate an explainer and quiz the user so they genuinely understand the change before merging (Thariq Shihipar's "quiz me before I merge"). Deliverable of this session is a settled design spec; implementation happens via `create-agent-skill`. A shareable buy-in variant for reviewers was part of the original candidate.

Tension noted: an earlier same-day decision was to trial the techniques manually before building skills from them. Planning now is compatible (spec can wait for validation); whether to build immediately is an open question for this session (resolved in Q7: hold).

## Question Log

### Q1: v1 scope

Context: Article describes three artifacts — explainer, quiz, buy-in doc.

Question: What does version 1 of the skill cover?

Recommendation: Explainer + quiz; defer buy-in doc (team-workflow-specific, unproven need, lazy philosophy).

Discussion: Quiz-only inverts Thariq's read-then-verify flow; all-three bakes in an unproven team artifact.

Conclusion: v1 = explainer + quiz. Buy-in doc deferred.

### Q2: Input source of truth

Context: Thariq runs it at the end of the implementing session; this repo values fresh-eyes review (working-with-agents #9) and durable records over session memory.

Question: What does the skill build the explainer/quiz from?

Recommendation: Diff as ground truth (working tree/branch vs base by default; user-specified range/PR accepted), enriched by the implementing session's context or an implementation-notes file when present, but never dependent on them.

Discussion: Session-only is useless after the session ends and has the worker grade its own account; diff-only discards real rationale for no gain.

Conclusion: Diff is ground truth; session context/notes enrich opportunistically; must work in a fresh session.

### Q3: Output medium and durability

Context: Thariq uses an HTML report; repo rules prefer notes files for durable records and require harness-portable skills.

Question: What form does the explainer take, and does it persist?

Recommendation: Markdown notes file for the explainer, quiz interactive in chat; HTML render only as optional enhancement.

Conclusion: As recommended. Explainer is a markdown file (durable, feeds future buy-in doc); quiz runs in conversation one question at a time via the ask-question tool when available; HTML is an enhancement, never a dependency.

### Q4: Quiz strictness and gate

Context: Thariq's rule is merge only after a perfect score; a skill can only declare readiness, not block a merge.

Question: Strict re-quiz loop, one scored round, or hard-gate framing?

Recommendation: Strict loop with advisory gate (perfect score bar, re-teach + fresh question per miss).

Discussion: User chose lighter ceremony over the strict loop, accepting the stated trade-off (partial understanding gets feedback, not forced closure). Mitigation kept: misses are re-taught with pointers, and a low score ends with a concrete "re-run after reading X" suggestion.

Conclusion: One round, scored feedback. Deliberate divergence from the article's strict loop.

### Q5: Boundaries with sibling skills (settled from repo, not asked)

Conclusion: Explains but never judges (code-review's job), never edits (document-code's job), never executes (verify's job). Cross-suggests document-code when confusion stems from unclear code; points to code-review when it notices suspicious behavior. Quiz questions are behavioral ("what happens if X"), never symbol trivia, to keep the score meaningful.

### Q8 (user refinement): Quiz focus and format

Context: After the session closed, the user sharpened the quiz design.

Conclusion: (1) Questions cover the behavior change only — what the system observably does differently — never implementation details (no "which function/file/pattern"). (2) Lightweight multiple-choice: "what happens when X?" with plausible behavioral options, administered via the ask-question tool. (3) The quiz's goal is to surface misunderstanding or missing understanding easily, fast, and lightweight — a detector, not a mastery gate. This retroactively grounds the Q4 one-round choice: a detector needs one cheap round, not a pass-perfectly loop.

### Q6: Name

Question: What is the skill called?

Recommendation: `explain-change` — repo's verb-object convention, names the primary artifact.

Conclusion: `explain-change`.

### Q7: Build timing

Context: Same-day earlier decision was to trial the article's techniques manually before building skills from them.

Question: Build now or hold the spec until the trial validates the need?

Recommendation: Hold; manually prompt an explainer + quiz after the next 1–2 substantial changes, build only if useful and repetitive.

Conclusion: Hold until trial validates. This spec makes the eventual build a short create-agent-skill task.

## Decisions

- v1 scope is explainer + quiz: buy-in doc deferred until team-sharing need is proven.
- Input is the code diff as ground truth, enriched by session context or implementation-notes when available: skill must work in a fresh session.
- Explainer is a durable markdown notes file; quiz is interactive in chat; HTML render is an optional enhancement only.
- Quiz is one round with scored feedback: misses re-taught with pointers, low score ends with a re-run suggestion; no forced loop (deliberate divergence from the article).
- Quiz is a lightweight misunderstanding detector, not a mastery gate: multiple-choice "what happens when X?" questions about the behavior change only, never implementation details, run via the ask-question tool.
- Boundaries: explain-only — no judging (code-review), no editing (document-code), no executing (verify); cross-suggest those skills when their territory appears.
- Name is `explain-change`: description triggers include "explain this change", "quiz me on it", "walk me through what changed", "before I merge".
- Hold the build until the manual trial validates the need: build via create-agent-skill from this spec afterwards.

## Implementation Sketch

For the future `create-agent-skill` build. Ordered by likelihood of revision — review the top items, trust the bottom.

1. Description / triggers (most likely to change — validate during the manual trial): "Explain a completed change and verify the user's understanding with a lightweight behavior quiz before merge. Use when the user asks to explain this change, walk me through what changed, quiz me on it, or wants a pre-merge understanding check. Not for judging code quality (code-review), adding comments (document-code), or runtime verification (verify)."
2. Explainer file convention (blocked on the implementation-notes trial): name, location, committed vs local — inherit whatever that trial settles.
3. Explainer content shape: what changed behaviorally, why (from session context/notes when present), what to watch for; written for the owner, structured so a buy-in variant could later be derived from it.
4. Workflow (stable): resolve target diff (working tree/branch vs base; accept explicit range or PR) → read enough surrounding code to understand behavior, plus session context/implementation-notes if present → write explainer file → quiz → scored feedback.
5. Quiz mechanics (settled, unlikely to change): 3-7 multiple-choice "what happens when X?" questions on the behavior change only, never implementation details; ask one at a time via the ask-question tool; one round; each miss re-taught with a pointer into the explainer/code; end with score, misunderstandings surfaced, and a re-run suggestion if the score was low.
6. Gotchas to encode: no judging/editing/executing; behavioral distractors must be plausible (no giveaway options); do not quiz on unchanged behavior; explainer must not assume the implementing session's context exists.

## Open Questions

- Buy-in doc variant: deferred until a real team-sharing need appears; the durable explainer file is designed to be its input when it does.
- Explainer file location/naming: follow whatever convention the implementation-notes trial settles (same family of kept notes files).

## Risks / Watchpoints

- Overlap creep: the explainer must not drift into code review (judging quality) or document-code (editing comments); it explains, only.
- A quiz that is easy to game (agent asks trivia, user pattern-matches) provides false confidence. Mitigation: behavioral questions only.
- One-round quiz is a deliberate divergence from the article's pass-perfectly loop; if trial shows low scores get ignored, revisit strictness.
