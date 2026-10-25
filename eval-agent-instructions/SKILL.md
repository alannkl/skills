---
name: eval-agent-instructions
description: Measure what a skill, AGENTS.md, CLAUDE.md or prompt does by running real sessions with and without it across harnesses, models and APIs, and report by rule and by change.
disable-model-invocation: true
---

# Eval agent instructions

A measured evaluation runs real, billed sessions with and without the instructions, grades them against expectations declared beforehand, and reports what the instructions change. Settle which question the user is asking before designing anything:

- **Does it help?** The artifact against no artifact.
- **Does a change regress?** The old and new text on the same cases.
- **Which rules matter?** The full artifact against a copy with one rule removed.
- **Does it trigger?** A skill description against should-trigger and near-miss requests.

## Runner

`scripts/eval_instructions.py` runs each agent session through Harbor in its own sandbox, or calls a model API directly, and grades on the host. The sandbox is bubblewrap where it is installed, seeing only the host's system files, the pinned agent CLIs and the task; elsewhere, or with `--env docker`, a Docker container. Under bubblewrap every session of every setup draws from one queue, the longest expected first, `--concurrency` at a time: by default up to 32, as many as free memory holds; a given number runs as given, with a warning when it will not fit; `CONFIG=N` caps one setup. Run it from the root of the repository that holds the artifact; `--help` lists its commands. It needs bubblewrap on Linux or Docker, `uv`, and credentials in the environment or in that repository's `.env`: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` for Claude Code, Codex, Anthropic and OpenAI API calls, and the judge, and `OPENROUTER_API_KEY` for OpenRouter setups. A setup is a harness, a model, a reasoning effort and, for OpenRouter models, the upstream providers: `--harness`, `--model`, `--effort` and `--provider` give one, and `--config` names a preset from `scripts/configs.json`, which also holds what each harness and model needs. Without either, a run uses the suite's `run` setups and `--full` its `full` setups, as `references/suites.md` describes, and a `--minus` run uses the `full` setups. Name a setup to measure the text on that model alone.

What it delivers, per `references/suites.md`:

- a skill, installed where each harness finds skills and named by path in the request of every arm that has it, so a run measures its text, not its description;
- an instruction file such as AGENTS.md or CLAUDE.md, placed in the workspace;
- a prompt: a system prompt passed to Claude Code or Codex, or sent with an API call, or a user prompt placed before the request. An app's prompt runs through the API, since no agent harness runs it in practice.

## Workflow

1. Scope the evaluation: the artifact and its path, the harnesses and models it must work on, and the question. When those setups differ from the defaults, name them in the suite's `eval.json`. Run edit rounds on the `run` setups with `--rule` for each rule the change touches, which selects the cases that test it, and a full evaluation with `--full --all-cases`. Removal decisions use every setup the artifact must support; a portability question uses every setup that matters.
2. Build or extend the suite in `evals/<suite>/` per `references/suites.md`. Choose cases from requests users make before seeing any results.
3. Before the first paid run, show the plan: cases, arms, setups, attempts, and the number of sessions. Start when the user agrees.
4. Probe each harness setup new to the suite with `--probe`, and confirm the artifact is visible in the with arm and absent in the without arm. A user prompt or an API call passes the text straight into the request and has no probe.
5. Run at least three attempts per arm, and treat the result as a first sample, not proof. To compare a draft with the current text, run it with `--artifact DRAFT --variants with` on the same cases and setups, regrade both sides with `--graders-from-repo`, then run `compare --baseline <runs of the current text> --candidate <draft run>`. It lists acceptance grades and work per run on both sides and every case and grader that dropped; `--pairwise JUDGE` adds a blinded judgment of whole outputs, for behavior no grader sees. Examine every new failure of a required outcome, whatever its count.
6. Check the runs before reading grades:
   - Infrastructure errors and runs Harbor never produced are not failures.
   - The report lists runs whose harness retried failed model calls; their time includes the provider's delay. Classify a run as infrastructure only from such evidence, never from its length: a skill that makes the agent search or polish more is slow for real.
   - A with-arm run that never loaded a skill tests triggering, not the skill's text.
   - A run that loaded a same-named skill from elsewhere is invalid.
   - An API call through a proxy may carry the proxy's own system text; read one transcript before trusting a bare-call result.
7. Read the grades per the sections below, then report.

## Reading results

- Report each harness and model pair separately; never pool runs across them.
- A case the baseline passes reliably cannot show improvement; report it as a regression guard, and as evidence that its rules may be no-ops.
- Before changing the text over a case that fails with the artifact, read the judge's reasons, then that case's result in both arms on each setup the artifact must support:
  - Passes with the artifact, fails without: the text works there. A failure on a setup the artifact need not support is that model's limit; keep the text.
  - Fails with the artifact, or its transcript misreads the rule: the wording is at fault, more surely when another setup misreads it too. Reword the existing text rather than adding to it.
  - Passes in both arms: the text changes nothing on this case for this setup.
  - Fails in both arms: look for evidence the fixture lacks, an ambiguous grader, or a tooling failure.

  When the judge is a setup's own model, check that setup's verdicts by hand.
- Read the transcript behind an undecided grade or a judge disagreement before counting it either way.

## Removing a rule

- A rule whose graders pass as often without the artifact as with it is a removal candidate, not a proven no-op.
- Remove a candidate only when no one can name the failure it prevents and why the executor's default would miss it, or when the copy without it (`--minus`) does as well as the full artifact on the cases that exercise it, over at least three runs per arm on every setup the artifact must support. Until then, keep it.
- A rule with no grader cannot be judged. Before deciding on one, write a realistic case where the rule applies and a grader for what it requires, confirm the full artifact passes, then run `--minus`.
- The report lists candidates with their evidence; removing text is an edit the user approves.

## Trigger checks

`--trigger` checks a skill's description: it runs the with arm alone, leaves the skill to trigger, and counts how often should-trigger cases and near-misses load it. Every case whose `expect_skill_loaded.with` is true is a should-trigger request; near-misses are cases marked `trigger_only`, which body runs leave out. Keep at least 8 of each, with varied phrasing, casual language, typos, file paths, and intent buried in a larger task. Run it on the old and new description and compare. When a boundary fails, fix the broader intent rather than the exact wording that failed.

## Report

Open with the answer to the user's question and the decision it supports. Then, for each setup:

- pass counts per case and arm, and the table from `rules` when the suite has a rule map;
- median work per run in each arm: agent time, tool calls, and input and output tokens, which show what the artifact adds to every run;
- removal candidates and untested rules;
- runs set apart: infrastructure errors, runs that never loaded the skill, undecided grades, judge disagreements;
- cost as the harnesses report it, naming setups that report none;
- what the sample size can and cannot show.

When the user authorizes changes, revise the instructions, then rerun the cases the change touches.
