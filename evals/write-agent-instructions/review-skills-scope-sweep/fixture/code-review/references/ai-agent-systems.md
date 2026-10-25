# AI / Agent Systems Review Overlay

Use this overlay when a change affects prompts, tool calls, model-visible context, memory, retrieval, agent state, delegation, evals, or generated output handling.

## Review Focus

- Intent and boundaries: confirm what the agent is allowed to decide, what must remain user-controlled, and which tools or data sources it may use.
- Prompt and context construction: check that user input, retrieved text, tool output, logs, and prior conversation are clearly delimited and cannot silently override higher-priority instructions.
- Context size and selection: look for unbounded concatenation, missing truncation, irrelevant retrieval, hidden token growth, and large model-visible fragments that should be summarized or filtered.
- Prompt-injection safety: check whether untrusted content can instruct the agent to reveal secrets, skip checks, alter tool choices, or treat external text as system/developer instructions.
- Tool safety: verify tool permissions, argument validation, destructive action gates, sandbox assumptions, idempotency, and whether failures or partial results are handled.
- State and resume behavior: check session compatibility, stale state, duplicated actions after retry/resume, lost user intent, and inconsistent handoff summaries.
- Output handling: check that model output is validated before execution, storage, display, or external submission; watch for code execution, HTML/script injection, unsafe file paths, and malformed structured output.
- Evals and tests: prefer behavior-level scenarios that exercise realistic prompts, adversarial input, tool failures, resume paths, and regression cases.

## Common Findings

- Untrusted retrieved content is inserted into the same instruction channel as trusted guidance.
- Tool calls accept model-generated paths, commands, identifiers, or URLs without validation.
- Agent state is persisted or resumed without enough versioning, deduplication, or intent confirmation.
- Tests assert a single happy-path response while missing tool failure, injection, or malformed-output cases.

Report only concrete failures or plausible triggers tied to the changed code. Do not require a full AI safety framework for a narrow prompt or eval change unless the touched surface creates that risk.
