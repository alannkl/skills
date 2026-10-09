---
name: retrospect
description: Find repeated corrections and friction in recent agent sessions across projects and harnesses, and turn the lessons the user picks into durable fixes where each belongs.
disable-model-invocation: true
argument-hint: "[project <path>] [since <date>]"
---

# Retrospect

Run bundled scripts by absolute path, using `<skill-dir>` for this skill's installed directory.

## Workflow

1. Index the window. Scope is every project unless the user names one.
   - Run `python3 <skill-dir>/scripts/collect-messages.py`. `--project <path>` keeps that directory and its subdirectories; `--since <ISO date or time>` overrides the window, which otherwise starts at the later of 14 days ago and the time in `~/.agents/retrospect-last-run`; `--slices <n>` sets the slice count (default 3); `--out <dir>` replaces the default `~/.tmp/retrospect/<UTC time>/`.
   - It reads Claude Code, Codex, Cursor CLI and Antigravity CLI logs read-only, keeps only messages the user typed, drops every session that invokes retrospect (this one included), and writes `slice-<n>.json` files, each holding its messages and the sessions active in its time range.
   - Stdout is a JSON summary: `window` (`since`, `until`, `source`), per-harness `status` (`read`, `absent`, `unrecognized`) with session, headless, subagent and unrecognized-file counts and known `limits`, `excluded_sessions`, message counts per project, and the slice files. Exit 2 means an unusable `--since`.
   - When a slice holds more than about 300 messages, rerun with more slices.
   - Never open the slice files or transcripts yourself; collectors read them.

2. Report coverage: the window and its source, each harness read or skipped with the reason, unrecognized files, and limits. An unrecognized harness is a coverage gap; never read its files by hand or guess their format. With no messages, report and go to step 8.

3. Mine. Load `delegate` and dispatch one collector per slice. Each work order names the slice file and `<skill-dir>/references/harness-logs.md`, and asks for these signals:
   - **Correction:** a typed message in the slice that redirects, rejects, or repeats an instruction the agent should already have followed.
   - **Friction**, needing no correction, from any transcript the slice lists, subagent and headless ones included: a long search for a file or fact; a mistake a lint, type check or test could have caught; expensive tool calls that could be streamlined; crucial information the agent could not reach, such as logs or read-only services.
   - **Workflow:** the user typing the same multi-step instructions or prompt in several sessions.
   - Collectors search for signals before reading and return per finding: harness, project, session, transcript path, time, signal kind, a one-line paraphrase without quoted chat text, and the candidate lesson; never raw transcript text.

4. Qualify lessons. Cluster findings across slices. A lesson qualifies when its pattern appears in two or more slices, or when it is one explicit correction that generalizes beyond its task.
   - Check each lesson against what is already persisted: the running harness's memory, the global and project instruction files (`AGENTS.md`, `CLAUDE.md`), and the text of the skills involved. A persisted lesson goes to the "already captured" list with where it is saved; if the window shows it still being violated, the lesson becomes why the saved rule did not hold.
   - For a repeated workflow, check the installed skills (`~/.agents/skills/`, `~/.claude/skills/`, the project's `.agents/skills/` and `.claude/skills/`) and both lock files first. A covering skill that did not trigger makes the lesson about its description or invocation, not a new skill.

5. Interview. Ask one short structured round, with the ask-question tool when available, to catch intent the logs missed: which lessons matter, misread evidence, and context behind a correction.

6. Propose, then stop for the user's pick; change nothing before it. For each lesson give the statement, evidence locations (harness, project, session, time), destination per Destinations, and the proposed fix. Order by severity: wrong or destructive results first, then repeated user corrections and rework, then wasted agent effort.
   - A mechanical violation (a fixed syntactic pattern, banned API, import shape, or file-location rule) gets a deterministic check such as a lint rule, hook or CI job; prose rules are for judgment calls only.
   - Before proposing a check, inspect the target's existing check commands and CI. An existing check that is unwired or silently broken is the finding, and a repo with no guardrail at all (no pre-commit hook and no CI running its checks) is a finding in itself.
   - An empty proposal list is a complete result.

7. Apply only the picked lessons; unpicked ones are not recorded and come back if they keep repeating. Load `create-agent-skill` to edit or create a skill, and `writing-for-agents` when installed to edit an instruction file. Make no commits, sends or other external actions.
   - Apply directly only when the session runs inside the destination repo or project; otherwise write a hand-off brief: destination repo and file, the lesson, the fix, how to check it, and for a skill, that the edit goes through `create-agent-skill`.
   - Anything written outside the project a lesson came from (skill source, the constitution, briefs for other repos) states the lesson generically: no project names, code or quoted chat text. Session locations appear only in the proposal list.

8. Report: coverage; lessons applied, with paths; briefs, ready to paste; lessons not picked; and the "already captured" list with where each is saved, which needs no pick.
   - After an all-projects run reaches this report, picked lessons or not, run `mkdir -p ~/.agents && printf '%s\n' <window.until> > ~/.agents/retrospect-last-run`. Skip it for runs narrowed by `--project`, runs whose `--since` started later than the default window, and aborted runs.

## Destinations

- **Universal collaboration rule:** the `constitution` skill's source file, by in-place compression, never by splitting or pruning.
- **Lesson about a skill:** the skill's source repo, never an installed copy under `~/.agents/skills/` or `~/.claude/skills/`. A skill listed in a lock file (`~/.agents/.skill-lock.json` globally, `<project>/skills-lock.json` per project, each entry under `skills.<name>` with `source`, `sourceUrl` and `skillPath`) is an installed copy: route to its source, naming `source` and `skillPath` in the brief. The session is inside the source repo when its git remote matches `sourceUrl`. A project skill not listed in a lock file is project source.
- **Project-specific lesson:** the project's environment. A check for a mechanical violation; its `AGENTS.md` only for what every session in the project needs; a project skill under `.agents/skills/` or `.claude/skills/` for a workflow or domain knowledge only some tasks need.
- **New skill:** a workflow repeated in two or more slices that no existing skill covers. A skill useful across projects goes to the user's skills source repo, one useful in a single project becomes a project skill. Name the skill, its job, and whether it should be user-invoked.
- **Personal preference:** the running harness's memory, flagged as visible to that harness only. If the harness has no memory, say so and ask for the destination.
