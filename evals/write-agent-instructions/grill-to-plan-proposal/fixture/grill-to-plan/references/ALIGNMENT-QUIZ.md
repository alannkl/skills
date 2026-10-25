# Alignment quiz

One round of multiple-choice questions checking that the user and the plan agree on how the planned system should behave. A misalignment detector, not a test: there is no wrong answer. An answer that differs from the plan means the user chose the behavior they expected, and the gap between their expectation and the plan's intent is a design finding to resolve.

## The round

- Ask "what happens when X?" questions about the planned system's behavior: edge cases, failure paths, defaults, interactions between components or steps.
- Target two kinds of behavior: what the user never explicitly reasoned through — agent-decided branches, bulk-accepted recommendations, consequences implied by settled decisions but never stated in the session — and the plan's critical paths, where a misalignment would be costly even though the user decided them directly; an early decision can drift out of the user's head as the plan evolves. Skip peripheral behaviors the user already decided — asking those detects nothing.
- The target sets the count — one question per behavior worth probing. If nothing qualifies, say so and skip the round; never pad with easy questions.
- Every option must be a behavior the plan could plausibly have chosen; exactly one is what the plan intends. Shuffle the intended option's position from question to question and keep options similar in length and detail.
- Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages.

## On divergence

- When the user picks an option other than the plan's intent, treat it as a surfaced design gap, not an error to correct.
- State what the plan intends and why that option was recommended over the behavior the user chose — concrete trade-offs, not a repeat of the plan text — then let the user decide: keep the plan's behavior or change the plan to match their expectation.
- A changed decision is a real decision: update the session record and `plan.md` like any other, and check whether dependent decisions need revisiting before closing.

## Close

- Summarize the gaps surfaced and how each was resolved: kept as planned, changed, or deferred as an open question.
- If no gaps surfaced, say the plan and the user's expectations line up and stop; that is a complete result.
