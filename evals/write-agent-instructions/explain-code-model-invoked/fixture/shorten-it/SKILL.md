---
name: shorten-it
description: Shorten text while preserving meaning, tone, nuance, and important details.
disable-model-invocation: true
---

# Shorten It

Shorten existing text without changing its job, claims, audience, or voice. Add nothing.

## Workflow

1. Preserve meaning first.
   - Keep intent, tone, nuance, claims, caveats, scope, names and identifiers, numbers, examples, technical terms, requirements, constraints, and steps unless clearly redundant. Redundant means cutting it breaks nothing; if something breaks, keep it or merge it.

2. Cut only low-value wording.
   - Remove repetition, filler, hedging, verbose transitions, and needless nesting.
   - Merge duplicated ideas, overlapping bullets, or overlapping paragraphs.
   - Keep the small words that carry structure; never trade clarity for word count. "Remove backup file" reads two ways; "Remove the backup file" reads one. Keep "that" where it forces a single parse, and keep "only" and "not" beside the word they change.

3. Return the shortened text.
   - Follow any requested length or format.
   - Change text only where a cut or merge happened.
   - Output only the shortened version.
   - If the requested length would require losing important meaning, say so briefly.
