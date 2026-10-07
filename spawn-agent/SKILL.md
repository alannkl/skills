---
name: spawn-agent
description: Spawn a headless coding-agent CLI run for one scoped subtask. Use when the user asks to delegate work to another agent instance, run an agent CLI non-interactively (such as Antigravity's `agy -p` or Cursor's `agent -p`), automate a headless agent in a script, build, or CI step, or fan work out across isolated sessions. Do not use for interactive agent sessions or when the host's own subagent, task, or agent tool already fits.
---

# Spawn agent

## Supported harnesses

| Harness                | CLI      | Reference                   |
| ---------------------- | -------- | --------------------------- |
| Google Antigravity CLI | `agy`    | `references/antigravity.md` |
| Claude Code            | `claude` | `references/claude.md`      |
| Cursor Agent           | `agent`  | `references/cursor.md`      |
| Codex CLI              | `codex`  | `references/codex.md`       |

If the user names a harness with no reference here, such as Gemini CLI, say it is unsupported and offer a supported harness.

## Workflow

1. Decide whether to spawn at all.
   - Spawn when the subtask needs an isolated context window; a different working directory, repository, or Git worktree; a scriptable CI or build step; or an agent host with no suitable built-in subagent.
   - Prefer the host's built-in subagent or task tool when it fits; it keeps the host's context and usually costs less.
   - Keep anything that needs interactive approval or a terminal UI in the host; headless runs cannot prompt a human.

2. Select the harness. Use the one the user named, then the host's own CLI if supported, then another installed supported CLI. Confirm it with `command -v <cli>`. If it is missing, stop and give the reference's installation guidance. Never install a CLI unprompted or substitute another harness silently.

3. Read the selected harness's reference and follow it for flags, permissions, output parsing, session resumption, and authentication. Headless interfaces vary by tool and release, so never invent flags from memory. Consult `--help` and the linked official docs only when the reference does not cover a behavior or after a flag or output failure. Do not use them as a routine preflight. Update the reference when it has drifted.

4. Make the subtask self-contained. Assume the spawned run has no conversation history. Put the goal, relevant paths, constraints, and exact expected output in the prompt. Pass large inputs as file paths, not inline text.

5. Pass behavior-affecting settings explicitly: model, permission mode, and directory access, per the reference. Headless runs inherit local settings, extensions, and project memory, so an identical command can behave differently across machines. When the caller or user requests lean mode, use the reference's lean-start flags and load an MCP server, skill, or extra tool only if the subtask names it.

6. Pre-authorize every tool the subtask needs with the reference's permission flags. A headless run cannot ask for approval. It may deny or skip an unapproved tool call and still report success, so under-granting can look like success. A fully unattended bypass grant also allows unrestricted shell and network access. Use one only in a sandbox, container, or disposable worktree, and say so.

7. Bound the run before starting it. Set the CLI's turn or iteration limit when available, and wrap the call in the host's timeout, such as `timeout 600 <cli> ...`. If edits must not touch the caller's checkout, run them in a disposable worktree or container and verify the result there.

8. Pick the output format the caller can parse: JSON for programmatic use, streaming for progress on long runs.

9. Run it with stdout and stderr captured to files and the exit code recorded, for example `timeout 600 <cli> ... > run.out 2> run.err; echo $?`. If authentication fails, stop and give the reference's login command. Never authenticate on the user's behalf or inline credentials in a command, settings file, or committed script.

10. Check the output protocol with the bundled verifier (Python 3, no dependencies), run by absolute path with `<skill-dir>` for this skill's installed directory: `python3 <skill-dir>/scripts/verify-run.py --harness <claude|codex|antigravity|cursor> --stdout run.out --stderr run.err --exit-code <code>`. It detects json or stream-json output, applies the reference's acceptance rules, writes the final response text to `<stdout>.result.txt` or `--result <file>`, and prints one JSON object: `status`, `reason`, `session_id`, `result_file`, `structured_output`, `permission_notices`, `stderr_tail`, and `usage`. For a run requested with text output, pass `--format text`, which checks only the exit code and non-empty output and yields no session id.
    - Exit 0 means the protocol completed. Inspect any `permission_notices` before trusting the run.
    - Exit 1 means the run failed, with the cause in `reason`: a non-zero or timeout exit code, malformed or incomplete output, a non-success status, a missing session or result, a denied tool call, or a Cursor sandbox startup error. A denied tool call means a grant from step 6 was missing: correct it and rerun instead of switching to a bypass mode.
    - Exit 2 means unusable input; an argument error prints usage instead of JSON.

11. Verify the task itself: a run can complete its protocol after doing no work. Before reporting success, confirm the artifact with `git status`, `git diff`, the relevant tests, or direct file inspection.

12. Continue a spawned conversation only through the reference's documented session-resume mechanism, with the `session_id` the verifier printed.

## Gotchas

- Tell the spawned run not to launch further agents unless the user requested nested delegation; nesting multiplies cost invisibly to the caller.
- Start long-lived servers from the host; background work a spawned run starts is torn down when the run ends.
