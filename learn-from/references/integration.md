# Integration

## Target discovery

Runs only when the user named no target and did not say there is none.

1. Take the user's question, or the study's question when a report was supplied, as the job to match.
2. Scan the current project only: skill descriptions, docs, plans, notes, instruction files, config. Read each candidate's stated purpose and constraints before ranking it.
3. Rank by overlap between the candidate's job and the question. Return at most three, each with: path, target type (artifact or idea), and one line on why it matches.
4. A clear match is one candidate whose stated job contains the question and no second candidate within reach of it. Everything else is several candidates or none.

## Proposal record

One per candidate idea. For target `none`, `current behavior` and `gap` read "not applicable"; every other field is filled against the proposed approach.

| Field | Content |
| --- | --- |
| `idea` | One sentence, in the target's vocabulary. |
| `support` | Independent families using it, and the claim IDs with their `basis`. |
| `current behavior` | What the target does now, with location, or "absent". |
| `gap` | The concrete failure or missed opportunity in the target, shown by an example or a location. |
| `expected improvement` | What changes for the target's user when the idea is adopted. |
| `added complexity` | Lines, branches, dependencies, or decisions the change adds. |
| `fit` | The user-stated or inferred preference the idea matches or violates, labeled as stated or inferred. |
| `check` | How the applied change will be shown to work. |
| `disposition` | `adopt`, `already satisfied`, `reject`, or `defer`. |
| `reconsider when` | For reject and defer: the evidence or condition that reopens the decision. |

## Output by target

- **Artifact**: a gap analysis, delivered as step 4 describes.
- **Idea**: a sharpened design. The idea restated part by part; for each part, what the sources did, which of the user's choices the shared practices back or contradict, and the decisions still open. Proposals attach to parts.
- **None**: a recommendation. The approach to take, the alternatives considered and why each was rejected, and a starting draft when the user asked for one or the approach is clear enough that the draft is cheaper than a description.

## Session evidence

Transcript claims carry the contract's `author`, `accepted`, and `outcome` fields. Authority follows them: a user correction and a verified outcome carry weight on their own; an assistant suggestion counts only when `accepted` is `adopted` and `outcome` is observed; repeated assistant suggestions across sessions are one voice, never several families. A `not recorded` acceptance limits what the claim says about endorsement, and a `not recorded` outcome limits what it says about effectiveness; neither changes the claim's `basis`.
