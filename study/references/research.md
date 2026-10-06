# Research

## Scout

Scouting finds candidates; it reads nothing closely. A subagent can run it and return the candidate list in its reply.

Work order:

- The question and its shape, and the sub-questions.
- Where to look: the user-named seeds, the ecosystems in scope, and whether web search is granted.
- Return per candidate: name; system family; surface or version; whether primary material is reachable and where; one line on how it differs from the other candidates.
- Budget in turns, and the instruction to do the work directly, without further delegation.

## Collect

One work order per collection unit:

- The unit's identity and the sub-questions it should answer.
- The [evidence contract](evidence-contract.md) in full, including the one-line claim template, and the instruction to return one source record in that shape.
- Reading rules: read the primary material first and cite its location for every claim; mark secondary material as secondary; record a mechanism the material does not mention as a gap, not as absent; record the surface and version each claim belongs to.
- Capability limits: read and search only; web fetch when granted, with a shell fetch such as `curl` as the fallback for hosts the fetch tool refuses.
- Budget in turns, and an early stop: when the last two reads added no new claim for the unit's sub-questions, stop and say so in the record.
- The instruction to do the work directly, without further delegation.
