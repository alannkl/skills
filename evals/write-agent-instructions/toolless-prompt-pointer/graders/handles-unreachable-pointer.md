---
type: llm
---

The deployed support agent has no tools and cannot read files, and the workspace has no code that assembles the prompt. The final message recognizes this. Pass if the style guide stays in the deployed prompt (possibly also copied to its own file for maintenance), or if the agent asks how the file's contents will reach the prompt before removing it. Fail if it removes the guide from `prompts/support_agent.md` and only notes that the application must include it later.
