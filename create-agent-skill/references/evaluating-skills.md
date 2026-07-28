# Evaluating Agent Skills

Use this reference only when the user asks to evaluate, prune, or iterate on an existing skill. Do not run these checks during the default skill-creation workflow; suggest them as an optional next step instead.

## Trigger Checks

- Create 8-10 should-trigger prompts and 8-10 near-miss prompts that should not trigger the skill.
- Include varied phrasing, casual language, typos, file paths, and cases where the skill intent is buried in a larger task.
- Revise the `description` if should-trigger prompts fail to load the skill or near-miss prompts load it too often.
- Avoid overfitting to exact failed prompt wording; fix the broader intent boundary.

## Output Quality Checks

- If the user wants eval files, start with 2-3 realistic cases in `evals/evals.json`.
- Each case should include `prompt`, `expected_output`, optional `files`, and later `assertions`.
- Compare with no skill for new skills, or with the previous version for revised skills.
- Grade assertions with concrete evidence. Use scripts for mechanical checks and human or LLM review for judgment-heavy qualities.
- Track time and token cost when practical; a skill should justify its context overhead.

## No-Op Pruning

- Test each sentence of `SKILL.md` in isolation: would the agent behave the same without it? A sentence the model already obeys by default only spends context.
- Delete whole failing sentences rather than trimming words from them; most prose that fails the test should go, not be rewritten.
- After pruning, re-run the trigger and output checks to confirm behavior held.

## Iteration Loop

1. Run realistic tasks with and without the skill.
2. Grade the outputs against concrete assertions.
3. Identify missed corrections, wasted steps, or unclear trigger boundaries.
4. Update `SKILL.md`, especially the description, workflow defaults, and `Gotchas`.
5. Repeat until the skill improves quality without adding unnecessary context cost.
