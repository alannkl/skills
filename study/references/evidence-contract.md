# Evidence contract

Version: `contract: 2`. Collectors produce source records in this shape, the synthesis cites their claim IDs, and `learn-from` cites the same IDs in its proposals. A report carries its `contract` line as the first line of its `Evidence records` appendix.

Compatibility: a consumer reads the version from the `contract` line wherever it appears; a `contract: 1` report has the same records, with the line at the top of the file. A consumer checks that the fields it needs are present and repairs missing ones for the claims it uses; it does not redo the study. A report with no `contract` line is legacy input and gets the same targeted repair.

## Study header

| Field | Content |
| --- | --- |
| `question` | One sentence. |
| `shape` | `subject` or `field`. |
| `sub-questions` | The list the stop test runs against; for a field, the comparison dimensions. |
| `date` | Date of collection. |
| `budget` | Source estimate, time, tokens, web access granted or not. |
| `sources` | Selected units with their family, and dropped candidates with the reason. |
| `coverage gaps` | Sub-questions or families the study could not reach, and why. |

## Source record

One per collection unit.

| Field | Content |
| --- | --- |
| `id` | Short slug used as the claim ID prefix, such as `codex-rubric`. |
| `identity` | Name, family, surface or version, URL or path, revision or retrieval date. |
| `access` | `primary` (the source's own code, prompts, docs, data, or writing), `secondary` (third-party coverage), or `none`. |
| `claims` | Claim records below. |
| `limitations` | What this unit cannot show: hosted product with unpublished prompts, documentation newer than the deployed version, and the like. |
| `gaps` | Sub-questions this unit left unanswered. |

## Claim record

| Field | Content |
| --- | --- |
| `id` | `<source id>:<n>`, stable for the life of the report. |
| `statement` | One sentence, in the source's own terms. |
| `location` | File and line, URL and anchor, or a short verbatim quote; precise enough to re-find. |
| `provenance` | `primary`, `secondary`, or `unverified`. |
| `basis` | `observed implementation`, `documented behavior`, `author-stated rationale`, `measured outcome`, or `analyst inference`. |
| `applicability` | Conditions under which the claim holds: product surface, scale, language, date. |
| `contradicts` | Claim IDs this claim disagrees with, if any. |

Collectors write each claim on one line:

```
<source id>:<n> | SQ<k> | <statement> | <location> | <provenance> / <basis> | <applicability> | contradicts: <ids or none>
```

Claims collected from a conversation transcript carry three more fields:

| Field | Content |
| --- | --- |
| `author` | `user`, `assistant`, or `tool output`. |
| `accepted` | `adopted`, `rejected`, `unanswered`, or `not recorded`. |
| `outcome` | What was observed after it was applied, `not applied`, or `not recorded`. |

## Report shape

Write the report for a reader who was not in the session. The body reads top to bottom without this contract: no claim lines, sub-question codes, working-directory paths, or process detail such as budget and collectors. The records go in an appendix.

Body:

1. A title naming the subject or question.
2. Summary: the question, the outcome (complete, partial, or blocked, with the reason when not complete), the two or three findings that matter most, and the coverage gaps that limit them.
3. Findings, by shape:
   - Field: agreements, each with the number of independent families behind it and what the counterexample search found; disagreements, naming who differs, on what, and the basis on each side; open questions.
   - Subject: how it works; design choices with their rationale, each marked as stated by the author or inferred; ideas worth carrying elsewhere; open questions.
4. Sources: every URL or path read or relayed, per unit, marked read, relayed, or unreachable, with the retrieval date.

Cite a claim by linking its location at the pinned revision, or by naming the file and revision when no link exists, followed by its claim ID: `([to-tickets](https://github.com/...#L38), mp:3)`. Before the first ID, tell the reader in one sentence that IDs point to the evidence records.

Appendix, titled `Evidence records`: the `contract` line, the study header, then one section per source record with every claim line, so each cited ID resolves.
