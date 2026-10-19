---
type: llm
focus: {source: file, path: prompts/support.ts}
---

Judge `prompts/support.ts`. The prompt now tells the agent never to promise or offer a refund above the configured limit, and it states that limit through `${POLICY.refundCap}` (with the currency), not a literal amount. The existing rules and the function signature `supportSystemPrompt(toolList: string[])` are unchanged in meaning, and the file is still valid TypeScript.
