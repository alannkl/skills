# ticket-classifier-prompt-trim

**Family:** 6 (trim an instruction file). **Artifact:** system prompt in Python backend code. **Domain:** ML/LLM ticket triage for a B2B SaaS.

**User:** backend/ML engineer who owns the triage service; cares about per-call tokens at 40k tickets/day and about not breaking routing.

**Why realistic:** classifier prompts accrete "Remember..." lines and repeated lists as people patch misclassifications. "Tighten it up, don't change the labels" is a typical ask.

**Good result:** a noticeably shorter SYSTEM_PROMPT that keeps the six category identifiers and meanings, the three urgency values and their criteria, the JSON keys, and each disambiguation rule; drops the repeated category list, the duplicate login rule, the duplicate JSON-only reminder, the "very important"/"expert" filler. Code outside the prompt unchanged.

**Plausible bad results:** dropping a disambiguation rule (e.g. the SSO-admin-vs-locked-out distinction, or the "used to work" exception) as if it were filler; renaming a label (e.g. `how-to`); dropping `confidence` (router uses it); moving the prompt to a new file; "fixing" the unrelated defect in `router.py` (no queue for `other`, so `QUEUES[c.category]` raises KeyError) without being asked. Mentioning that defect in the reply is fine.

**Judgment calls:** keeping or dropping "Think carefully... take your time" both pass. Keeping or dropping the example JSON both pass. `response_format=json_object` already forces JSON, so trimming the no-code-fences line is fine but not required. The shortness grader asks for a material reduction with every decision's meaning intact; leftover avoidable repetition counts against it as evidence of poor compression, not as an exact-once rule, and a brief example may stay. The code-behaviour grader judges meaning only; the parser tests in `tests/` say nothing about classification behaviour.
