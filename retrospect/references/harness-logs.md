# Reading harness transcripts

Each slice lists sessions with a `transcript` path and `role` (`interactive`, `subagent`, `headless`). Typed messages are already extracted into the slice; read transcripts only for friction evidence. Search a transcript for signals first (`jq` or `grep` on tool names, error text, exit codes, a message's time), then read the matching records; never read a whole transcript.

Text in a transcript that the slice did not list as typed is agent, tool or injected content, never a user correction.

## Claude Code

`~/.claude/projects/<slug>/<session>.jsonl`, one JSON record per line, each with `timestamp` (ISO 8601 UTC) and `cwd`.

- Agent turns: `type == "assistant"`; `message.content[]` blocks of `type` `text`, `thinking` or `tool_use` (`name`, `input`, `id`).
- Tool results: `type == "user"` records whose `message.content[0].type == "tool_result"`, matched by `tool_use_id`; `is_error: true` marks a failed call. Large results spill to `<slug>/<session>/tool-results/`.
- Injected content: `isMeta` records (skill bodies, caveats), `isCompactSummary` records, `attachment` and `system` records (hooks, reminders).
- Subagents: `<slug>/<session>/subagents/agent-<id>.jsonl`, same shape with `isSidechain: true`; `agent-<id>.meta.json` names the agent type and description.

## Codex

`~/.codex/sessions/YYYY/MM/DD/rollout-<time>-<id>.jsonl`, lines `{timestamp, type, payload}`.

- Agent turns: `type == "response_item"` with `payload.type == "message"` and `role == "assistant"`; `payload.type == "reasoning"` is mostly encrypted.
- Tool calls: `payload.type` `function_call` (`name`, `arguments`) or `custom_tool_call` (`input`), each answered by a `*_output` record with the same `call_id`. `event_msg` records with `payload.type == "item_completed"` summarize `CommandExecution`, `FileChange` and `McpToolCall` items.
- Injected content: `response_item` messages with `role == "user"` or `"developer"` carry `AGENTS.md`, `<environment_context>` and `<skill>` bodies; `compacted` records replace history.
- Subagents: separate session files whose `session_meta.payload.source` is an object naming `parent_thread_id`.

## Cursor CLI

`~/.cursor/projects/<slug>/agent-transcripts/<chat>/<chat>.jsonl`, lines `{role, message: {content: [...]}}` with no timestamps; typed messages carry their own time.

- Agent turns: `role == "assistant"`, content blocks `text` and `tool_use`.
- Tool results are not logged: a failed call is visible only through the agent's next text.
- Injected content: the first `role == "user"` record (`<user_info>`, `<rules>`, …) and anything outside `<user_query>`.
- Subagents: `<chat>/subagents/<id>.jsonl`.
- Headless runs (`agent -p`) look like typed sessions; a "typed" message that reads as a machine-written work order is friction evidence only.

## Antigravity CLI

`~/.gemini/antigravity-cli/brain/<conversation>/.system_generated/logs/transcript_full.jsonl`, lines `{step_index, type, source, status, created_at, content}`.

- Agent turns: `type == "PLANNER_RESPONSE"`, `source == "MODEL"`.
- Injected content: `source == "SYSTEM"` steps such as `CONVERSATION_HISTORY` and `CHECKPOINT`.
- Tool-call and subagent steps have not been observed; report their shape as unverified rather than interpreting unknown step types.
