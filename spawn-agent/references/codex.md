# Codex CLI (`codex exec`)

## Environment inheritance

- Codex loads user and trusted-project configuration, project instructions, skills, plugins, hooks, and MCP servers. Explicitly pass the model, working directory, sandbox, and approval policy.
- Use `--cd <path>` for the primary workspace and repeat `--add-dir <path>` only for extra writable roots the task needs.
- Pass `--model <model-id>` explicitly. Use the model the caller requested or one known to be available in the target environment; do not copy an ID from an example.
- Add `--strict-config` so unknown configuration fields fail before the run starts.
- Use `--ignore-user-config` or `--ignore-rules` only in controlled automation that must exclude those inputs. `--ignore-rules` excludes execpolicy `.rules` files, not project instructions.

## Permissions

- Set `approval_policy="never"` with `-c` so a headless run fails closed instead of waiting for human approval. Never use an interactive approval policy in unattended automation.
- `--sandbox read-only` for analysis; `--sandbox workspace-write` for edits. Workspace-write does not grant network access by itself.
- Add `--add-dir` for a required writable path outside the main workspace instead of broadening the whole sandbox.
- `--sandbox danger-full-access` removes the sandbox entirely; `--dangerously-bypass-approvals-and-sandbox` is the fully unattended bypass grant.
- Do not use the deprecated `--full-auto` compatibility flag; select the sandbox explicitly.

## Output

- Without `--json`, Codex writes progress to stderr and the final agent message to stdout. Use this only when a human or a simple pipeline needs the final text.
- Use `--json` for programmatic callers. It emits JSONL events, not one JSON object. Ignore unknown event fields.
- Capture `thread_id` from `thread.started`. Accept the run only after `turn.completed`. Reject `turn.failed`, `error`, malformed streams, and streams that end without a terminal event.
- `--output-last-message <path>` when a caller needs the final message in a file. `--output-schema <path>` when the final response must conform to a JSON Schema.

## Resume

- `codex exec resume` rejects `--cd`, `--sandbox`, and `--add-dir`. Set its sandbox with `-c 'sandbox_mode="workspace-write"'`.
- Continue a recorded session with `codex exec resume <session_id> "<follow-up>"`. Use `codex exec resume --last "<follow-up>"` only for the most recent session in the current working directory.
- Resume from the same working directory unless the caller intentionally targets another session scope. Add `--all` to `--last` only when it must consider sessions outside the current directory's history.
- Do not use `--ephemeral` when the run may need to resume; ephemeral runs do not persist session files.

## Templates

Set `codex_model_id` to a model available in the target environment.

```bash
codex_model_id='replace-with-an-available-model-id'

# One-off scoped task, read-only JSONL. `</dev/null` closes stdin — see gotchas.
timeout 300 codex exec --cd "$PWD" --model "$codex_model_id" \
  --sandbox read-only -c 'approval_policy="never"' --strict-config --json \
  "Summarize the public API of src/auth.ts in under 10 bullet points" </dev/null

# Pipe context in while keeping the instruction explicit
git diff main | timeout 300 codex exec --cd "$PWD" --model "$codex_model_id" \
  --sandbox read-only -c 'approval_policy="never"' --strict-config --json \
  "List typos in this diff as filename:line, nothing else"

# Apply a bounded edit in the selected workspace
timeout 900 codex exec --cd "$PWD" --model "$codex_model_id" \
  --sandbox workspace-write -c 'approval_policy="never"' --strict-config --json \
  "Fix the failing tests in tests/unit; do not change public APIs and do not spawn other agents" </dev/null

# Request a schema-constrained final response
timeout 300 codex exec --cd "$PWD" --model "$codex_model_id" \
  --sandbox read-only -c 'approval_policy="never"' --strict-config \
  --output-schema ./schema.json --output-last-message ./result.json \
  "Extract the exported function names from src/index.ts"

timeout 900 codex exec resume --model "$codex_model_id" \
  -c 'approval_policy="never"' -c 'sandbox_mode="workspace-write"' \
  --strict-config --json "$thread_id" "Continue the task"
```

## Authentication

- An authentication-required error is fixed by the user running `codex login`.
- In CI, let the existing secret manager expose `CODEX_API_KEY` only to the `codex exec` process.
- Install docs: <https://learn.chatgpt.com/docs/codex/cli>.

## Codex-specific gotchas

- `codex` without `exec` launches the interactive terminal UI. Always use `codex exec` for a headless subtask.
- Codex requires a Git repository by default. Use `--skip-git-repo-check` only when the caller intentionally selected a safe non-repository directory.
- If the prompt is omitted or is `-`, Codex reads the prompt from stdin. When stdin is piped alongside a prompt argument, Codex appends it as context.
- A non-TTY stdin without EOF hangs the run: even with a prompt argument, Codex waits on "Reading additional input from stdin..." until stdin closes. Background shells and job runners often hand the process an open stdin that never closes, so a headless run must end with `</dev/null` unless it deliberately pipes context in.
- `codex mcp-server` exposes Codex as an MCP server; it does not run a subtask. Call `codex exec` directly.
- Official docs: <https://learn.chatgpt.com/docs/non-interactive-mode> and the [`codex exec` command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-exec). Resume flags not listed here: `codex exec resume --help`.
