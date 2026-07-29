---
name: handoff
description: Create a compact handoff document so another agent can continue the current conversation.
disable-model-invocation: true
---

# Handoff

Create a temporary Markdown checkpoint for a fresh agent. The checkpoint complements durable project artifacts; it does not replace or repeat them.

## Workflow

1. Establish the next-session focus.
   - Treat any arguments as the user's description of what the next session will focus on.
   - Tailor the handoff's priorities, suggested skills, and first actions to that focus.
   - When no arguments are supplied, infer the immediate continuation goal from the current conversation. Label material uncertainty instead of inventing intent.

2. Gather only continuation context.
   - Summarize the current objective, verified progress, unresolved decisions, blockers, relevant constraints, and the exact next actions.
   - Distinguish verified facts from inferences and assumptions. Record checks already run and their outcomes so the next agent does not repeat work unnecessarily.
   - When workspace state is relevant to the handoff, inspect it live rather than relying on an earlier conversational description.
   - Find existing specs, plans, ADRs, issues, session records, commits, and diffs that already contain project knowledge. Reference each relevant artifact by path, commit identifier, or URL and say briefly why it matters.
   - Do not copy or paraphrase content already captured in those artifacts. Include only the small amount of context needed to explain why the next agent should open them.
   - Do not turn the handoff into a durable decision record. If knowledge needs to survive beyond this continuation, reference the durable artifact that owns it or identify the missing artifact as follow-up.

3. Redact sensitive information before writing.
   - Remove secrets and credentials, including API keys, tokens, passwords, private keys, cookies, connection strings, and sensitive environment values.
   - Remove personally identifiable information that is not essential to continuing the work.
   - Replace removed values with specific markers such as `[REDACTED: API token]`; never preserve a prefix, suffix, or other fragment that could aid recovery.
   - Treat command output, URLs, local paths, logs, diffs, and quoted conversation text as possible sources of sensitive data.
   - Preserve safe secret names or configuration keys only when the next agent needs to know that a value must be supplied.

4. Write the document with these sections:
   - `# Handoff`
   - `## Next-session focus` — the supplied arguments or the inferred continuation goal.
   - `## Current state` — objective, verified progress, and what remains.
   - `## Referenced artifacts` — paths, commit identifiers, or URLs with one-line reasons to read them. Write `None` when there are none.
   - `## Continuation notes` — constraints, assumptions, unresolved decisions, blockers, and verification results not already owned by a referenced artifact.
   - `## Suggested skills` — exact skill names and one-line reasons the next agent should invoke them. Suggest only skills relevant to the focus and evidenced in the conversation or discoverable in the environment; do not invent skill names. Write `No special skills suggested` when none apply.
   - `## First actions` — a short, ordered list of concrete steps for the next agent.

5. Save it outside the workspace.
   - Resolve the user's OS temporary directory from the platform's standard mechanism or environment setting. Do not create a `tmp` directory inside the workspace.
   - Use a collision-resistant Markdown filename beginning with `handoff-`.
   - Write only the handoff document to that file. Do not modify workspace files as part of this skill.

6. Validate before responding.
   - Re-read the saved file and scan it for unredacted secrets, credentials, personal data, and sensitive URL parameters.
   - Confirm the file exists, is readable, has all required sections, and is located in the OS temporary directory rather than the current workspace.
   - Confirm each referenced local artifact exists. Mark an external URL you could not verify as unverified rather than presenting it as checked.
   - Confirm the document does not duplicate the substance of referenced artifacts.

## Response Format

Return the saved document first as a clickable file link when the interface supports local links; otherwise return its absolute path. Do not reproduce the handoff document in chat.

Then provide exactly one copyable fenced block based on this instruction, filled with the actual path and focus:

```text
Continue this work from the handoff document at `<absolute temporary path>`. Read it first, then inspect the referenced artifacts instead of asking me to repeat their contents. Invoke the skills listed under "Suggested skills" when they are available. Focus this session on: <next-session focus>.
```

Do not add a second summary that competes with the saved handoff.

## Gotchas

- A handoff is ephemeral routing context, not a substitute for a spec, plan, ADR, issue, commit, or diff.
- Do not expose a secret merely because it appeared earlier in the conversation or repository history.
- Do not silently omit failed checks, open questions, or uncommitted work that changes how the next agent should proceed.
- Do not suggest every available skill; include only those that materially help the stated next-session focus.
- Do not save the handoff under the current workspace, even when the workspace already contains a temporary directory.
