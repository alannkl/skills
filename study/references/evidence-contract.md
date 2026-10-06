# Evidence contract

Version: `contract: 1`. Collectors produce source records in this shape, the synthesis cites their claim IDs, and `learn-from` cites the same IDs in its proposals. A study report opens with its `contract` line.

Compatibility: a consumer checks that the fields it needs are present and repairs missing ones for the claims it uses; it does not redo the study. A report with no `contract` line is legacy input and gets the same targeted repair.

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
| `access` | `primary` (the system's own code, prompts, docs, or engineering writing), `secondary` (third-party coverage), or `none`. |
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

Every report opens with a TL;DR: the question, the terminal outcome (complete, partial, or blocked) with the reason when it is not complete, the two or three findings that matter most, and the coverage gaps that limit them. Below it, section order may change; every field above must be present. Per-source detail goes after the synthesis. Both shapes end with the sources: every URL or path read or relayed, per unit, marked read, relayed, or unreachable, with the retrieval date.

Field study:

1. Question and trust: the header, with how far each source can be trusted and the coverage gaps.
2. Shared practices: each counted by independent families, citing claim IDs, with the counterexample search's result.
3. Disagreements: who differs, on what, and which basis each side rests on.
4. Open questions.
5. Per-source detail: one section per source record.
6. Sources.

Subject study:

1. Question and trust.
2. How it works: the mechanism, citing claim IDs.
3. Design choices and their stated rationale, each marked as author-stated or inferred.
4. Notable ideas worth carrying elsewhere.
5. Open questions.
6. Source record and sources.
