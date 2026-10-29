# Evaluating instructions

Use the section that fits the request; this is not a suite to run in full. Pruning while drafting, under step 5 of `SKILL.md`, needs none of these checks unless an evaluation condition in `SKILL.md` applies. A consequential authorized change gets one bounded check without a separate evaluation request; when the executor cannot run it, report the check and why it did not run.

## Behavior checks

- For a consequential change, write a scenario that exercises the changed requirement and declare beforehand what the output must show. Run the previous and revised versions on it; compare a new artifact with running no instructions. Run each in a fresh context so the evaluator's own context does not leak into the result.
- Grade against the declared expectations with concrete evidence. Use scripts for mechanical checks and human or LLM review for judgment-heavy qualities.
- Use one scenario per consequential change; add another only for a material risk the first cannot exercise.
- Check that every run loaded only the copy under test; an installed or built-in skill with the same name can shadow it.

## No-op disputes

- When reviewers disagree about whether a sentence changes behavior, run a bounded check with and without the sentence on the target executor instead of debating it. Whether a sentence is a no-op depends on the executing model and harness.
- A check that shows no difference does not prove a no-op; keep the sentence.
- A word too weak to beat the default is a no-op too. Treat a stronger word as a hypothesis to test, not a fix.

## Trigger checks

For descriptions and pointers an agent follows on its own:

- For an explicit evaluation, create 8-10 should-trigger prompts and 8-10 near-miss prompts that should not trigger the instructions. For a changed description or pointer condition, use a few of each that exercise the change.
- Include varied phrasing, casual language, typos, file paths, and cases where the intent is buried in a larger task.
- Revise the description or pointer if should-trigger prompts fail to load it or near-miss prompts load it too often.
- Avoid overfitting to exact failed prompt wording; fix the broader intent boundary.
- Label a review of the description against prompts as a static routing review, not a measured activation rate.

## Rushed done-conditions

When a step's done-condition is irreducibly fuzzy and runs show the agent rushing past it, first sharpen the bound; that fix is local and cheap. Only if sharpening fails, split the sequence so the later steps sit behind a real context boundary: a new session or a subagent that does not inherit the earlier conversation.
