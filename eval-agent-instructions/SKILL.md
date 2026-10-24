---
name: eval-agent-instructions
description: Measure what a skill, AGENTS.md or CLAUDE.md does by running real agent sessions with and without it across harnesses and models, and report by rule and by change.
disable-model-invocation: true
---

# Eval agent instructions

A measured evaluation runs real, billed agent sessions with and without the instructions, grades them against expectations declared beforehand, and reports what the instructions change. Settle which question the user is asking before designing anything:

- **Does it help?** The artifact against no artifact.
- **Does a change regress?** The old and new text on the same cases.
- **Which rules matter?** The full artifact against a copy with one rule removed.
- **Does it trigger?** A skill description against should-trigger and near-miss requests.

## Runner

`scripts/eval_instructions.py` runs each session in its own Docker container through Harbor and grades on the host. Run it from the root of the repository that holds the artifact; `--help` lists its commands. It needs Docker, `uv`, and credentials in the environment or in that repository's `.env`: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` for Claude Code, Codex and the judge, and `OPENROUTER_API_KEY` for OpenClaw setups that use OpenRouter. Setups are named in `scripts/configs.json`; without `--config`, a run uses `openclaw-deepseek-high`.

It delivers a skill, installed where each harness finds skills, or an instruction file, placed in the workspace under the name the harnesses read. For a system, developer, or task prompt, report that the runner cannot deliver it.

## Workflow

1. Scope the evaluation: the artifact and its path, the harnesses and models it must work on, and the question. Removal decisions use the weakest setup the artifact must support; a portability question uses every setup that matters.
2. Build or extend the suite in `evals/<suite>/` per `references/suites.md`. Choose cases from the behavior in question before seeing any results.
3. Before the first paid run, show the plan: cases, arms, setups, attempts, and the number of sessions. Start when the user agrees.
4. Probe each setup new to the suite with `--probe`, and confirm the artifact is visible in the with arm and absent in the without arm.
5. Run at least three attempts per arm, and treat the result as a first sample, not proof. To compare two versions of the text, run the with arm (`--variants with`) on each version with the same cases and setups.
6. Check the runs before reading grades:
   - Infrastructure errors and runs Harbor never produced are not failures.
   - A with-arm run that never loaded a skill tests triggering, not the skill's text.
   - A run that loaded a same-named skill from elsewhere is invalid.
7. Read the grades per the sections below, then report.

## Reading results

- Report each harness and model pair separately; never pool runs across them.
- A case the baseline passes reliably cannot show improvement; report it as a regression guard.
- When no version passes, find the cause before blaming the instructions: model capability, evidence the fixture does not supply, an ambiguous grader, or a tooling failure.
- A weaker model is a cheap regression screen, but its failures on judgment-heavy behavior can reflect capability rather than the instructions.
- Read the transcript behind an undecided grade or a judge disagreement before counting it either way.

## Removing a rule

- A rule whose graders pass as often without the artifact as with it is a removal candidate, not a proven no-op.
- Remove a candidate only when no one can name the failure it prevents and why the executor's default would miss it, or when the copy without it (`--minus`) does as well as the full artifact on the cases that exercise it, over at least three runs per arm on the weakest setup the artifact must support. Until then, keep it.
- A rule with no grader cannot be judged. Before deciding on one, write a case that tempts the failure the rule prevents and a grader that catches it, confirm the full artifact passes, then run `--minus`.
- The report lists candidates with their evidence; removing text is an edit the user approves.

## Trigger checks

For a skill description, write 8-10 should-trigger requests and 8-10 near-misses as cases, with varied phrasing, casual language, typos, file paths, and intent buried in a larger task. Run the with arm only on the old and new description and compare how often each loads the skill. When a boundary fails, fix the broader intent rather than the exact wording that failed.

## Report

Open with the answer to the user's question and the decision it supports. Then, for each setup:

- pass counts per case and arm, and the table from `rules` when the suite has a rule map;
- removal candidates and untested rules;
- runs set apart: infrastructure errors, runs that never loaded the skill, undecided grades, judge disagreements;
- cost as the harnesses report it, naming setups that report none;
- what the sample size can and cannot show.

When the user authorizes changes, revise the instructions, then rerun the cases the change touches.
