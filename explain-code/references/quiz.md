# Quiz

Run one round of multiple-choice questions on the target's missable behavior, then score and re-teach.

## The round

- Ask multiple-choice questions about what the target code observably does — "what happens when X?" is the typical shape.
- Quiz only non-obvious, easy-to-miss behavior: edge cases, failure paths, defaults, interactions between components or changes. Hard because the behavior is easy to miss, never because the question is tricky or hinges on incidental details. Skip anything already obvious from the explainer's summary or the user's own request — a question answerable without thinking detects nothing.
- No quota: the target sets the count — one question per genuinely missable behavior, done when each is covered. If the target offers none, say so and skip the quiz; never pad the round with easy questions.
- Every option must be a plausible behavior. No symbol trivia (never "which function/file/pattern"), and for change scope no questions about unchanged behavior.
- Shuffle the correct option's position from question to question, and keep all options similar in length and detail; a fixed slot or a longest-option-wins pattern is a tell.
- Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages. Confirm right or wrong in one line after each answer; save re-teaching for the end of the round.

## Score and re-teach

- After the round, report the score and each misunderstanding surfaced.
- For each miss, re-explain the behavior with a pointer into the explainer or the code.
- A miss can indict the code as well as the reader: when the user's expectation was reasonable and the actual behavior looks like a bug or a trap, note that in one line and suggest a code review — the re-teach still covers what the code does today.
- Leave any re-quiz to the user. If the score was low, end with a concrete suggestion: re-read the named explainer sections or code, then re-run the skill.
