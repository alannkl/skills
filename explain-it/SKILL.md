---
name: explain-it
description: Explain any non-code target — a concept, a document (paper, RFC, spec, policy), a design, a process, or a decision — until the user genuinely understands it, with optional follow-up Q&A, a quiz that surfaces understanding gaps, and an interactive micro-world for hard-to-hold dynamics. Use when the user asks to explain, teach, break down, walk through, or help them understand a topic or a provided document, or says they don't get something. Do not use for source code or code changes, quick factual questions that need a direct answer, pure summarization, or critiquing and rewriting a text.
---

# Explain It

Help the user genuinely understand any non-code target — a concept, a document, a design, a process, a decision. Present an explainer of what the target is, says, or does; the explainer is the deliverable. Three optional mechanisms sit on top: a Q&A session for what the explainer left open, a quiz — a misunderstanding detector, not a mastery gate — that surfaces missing or wrong understanding fast and cheaply, and a micro-world — a small interactive simulation for dynamics that prose and diagrams cannot make felt.

## Boundaries

- Explain only. Never judge the target's quality — a paper's rigor, a document's drafting, a design's soundness. If something looks wrong or weak while reading, note the observation in one line and suggest a separate critique or review pass; do not develop it into findings.
- Never revise the target. A user who wants the text improved is asking for a revision pass, not an explanation; say so.
- If the target is source code or a code change, use a code-focused explainer when available; otherwise adapt this workflow with the code as the artifact.
- Never fill a gap with confident invention. Every claim is attributed: the artifact, general knowledge, inference, or "not established".

## Workflow

1. Resolve the target and its grounding; state both in one line at the top of the explainer so a misread surfaces immediately.
   - **Artifact-backed**: the user supplies or points to the thing itself — a paper, RFC, spec, contract, policy, dataset, diagram, transcript. The artifact is the ground truth; read the relevant whole before explaining, and if it cannot be accessed, say so and stop rather than explaining from its title or reputation.
   - **Knowledge-backed**: a concept, technique, theory, or event with no artifact — "explain Raft", "explain how options pricing works". Ground it in general knowledge; verify load-bearing claims that are recency-sensitive or contested with web search when available, and label them uncertain when verification is not possible.
   - **Mixed**: an artifact about a broader topic. Keep the two grounds visibly distinct: what the document says stays attributed to the document; surrounding context comes labeled as general knowledge.
   - When the request is ambiguous ("explain this"), infer from context — pasted text or an open file means artifact-backed, a bare topic means knowledge-backed — and say what you resolved.

2. Calibrate to the reader. What the explainer must cover depends on why the user wants it — to decide, to apply, to follow a discussion — and on what they already know. Infer both from the conversation; when the answer would change the explainer materially and the session is interactive, ask one short question; otherwise pick a level, name it, and let the user correct it.

3. Understand before explaining. Read the artifact — or assemble the knowledge — at the altitude of the ask: what the target is, how it works or what it claims, why it is the way it is, and where its limits are. For an argumentative artifact (paper, proposal, ruling), that includes the claim, the support, and what the author concedes; for a mechanism (protocol, process, model), the moving parts, the flow, and the edge behaviors.

4. Present the explainer in chat. Do not write it to a file. Order it for comprehension:
   - Background first: the context needed to follow the rest, scaled to the reader from step 2. Never open with the details.
   - Intuition before details: state the essence in a few sentences and walk one concrete example — a real case, or a minimal toy world that keeps only what makes the mechanism visible. Walk a second, contrasting example only when the boundary between behaviors is the hard part. When the target invites a natural-but-wrong reading, name that reading and correct it; dislodging the wrong model beats stating the right one beside it.
   - Then the details, in the order that serves understanding — a paper's argument, a protocol's phases, a process's steps — never a section-by-section inventory of the artifact.
   - Attribute as you go: what the artifact says, what is general knowledge, what you infer, what is contested or unsettled.
   - Use a diagram (sequence, state, flow, component, timeline) whenever it beats prose; write diagrams in mermaid. Never diagram what a sentence covers.
   - Write it for the user, but keep it self-contained enough to reuse verbatim as a study note or a shared team explainer.
   - Make every offer at once, so nothing is lost if the user leaves after reading: a Q&A session (step 5), a durable home for the explainer (step 6), the quiz (step 7), and — only when step 9 warrants one — a micro-world. Present them as one numbered list — number only the options actually offered, with no gaps — and invite replies by number alone: "1", "2 3", or "all".
   - Then stop and let the user read. Run only what the user accepts, in step order when several are picked.

5. Run a Q&A session when the user opts in: answer follow-up questions until the user is satisfied.
   - Same grounding as the explainer: re-read or widen when a question exceeds what was read; distinguish artifact, knowledge, and inference; never fill a gap with a guess.
   - Match the answer's altitude to the question — a "why" gets the mechanism or argument traced, not a restated explainer section.
   - When a question reveals the explainer skipped something load-bearing, answer it and note the gap; fold it in if the user later accepts the durable-home offer.
   - When the session winds down, restate any offers from step 4 the user has not yet answered.

6. Give the explainer a durable home: write on acceptance, and if the step 4 offer is still unanswered when the session winds down, restate it before closing.
   - Name the concrete destination where it belongs — a notes file the user keeps, a team wiki page, a README or docs section when the topic serves a project — not a vague "this could be saved".
   - Never write it anywhere unasked. On acceptance, adapt it to the destination's audience rather than pasting verbatim, fold it into existing coverage rather than appending a duplicate, and carry the diagrams over.

7. Quiz the user when they opt in, one round.
   - Ask multiple-choice questions about what the target actually says, does, or implies — "what happens when X?", "what would the author say about Y?", "which case does this rule cover?".
   - Quiz only non-obvious, easy-to-miss substance: boundary cases, exceptions, the step everyone skips, the claim that sounds like the popular simplification but isn't. Hard because it is easy to miss, never because the question is tricky or hinges on incidental detail. Skip anything obvious from the explainer's summary or the user's own request.
   - No quota: ask the minimum that covers the genuinely missable — often just two or three questions. If the target offers none, say so and skip the quiz; never pad the round with easy questions.
   - Every option must be plausible. No trivia — never "which section/author/year" — and no questions a reader could answer without having understood.
   - Shuffle the correct option's position from question to question, and keep all options similar in length and detail; a fixed slot or a longest-option-wins pattern is a tell.
   - Ask one question at a time. Use the ask-question tool when available; otherwise ask as plain numbered chat messages. Confirm right or wrong in one line after each answer; save re-teaching for the end of the round.

8. Score and re-teach.
   - After the round, report the score and each misunderstanding surfaced.
   - For each miss, re-explain with a pointer into the explainer or the artifact.
   - Do not force a re-quiz. If the score was low, end with a concrete suggestion: re-read the named sections, then re-run the skill.

9. Build a micro-world when warranted and opted into: a tiny interactive simulation the user inhabits to feel the dynamics work.
   - Warranted only for dynamics hard to hold by reading — algorithms and protocols, probability and statistics, feedback loops and compounding, auctions and game-theoretic interactions, geometric or spatial reasoning. If the target reads fine, skip it entirely and do not offer one; prose, examples, and mermaid come first.
   - Build a single self-contained HTML file — embedded CSS and JavaScript, no external dependencies — that simulates just the target dynamics with example data and lets the user probe them: scrub steps, drag inputs, toggle branches, watch the result change.
   - Derive the simulation from the explained target and name every simplification — it models the idea; it proves nothing about the real world.
   - Every control must answer a "what happens if" question the user could actually ask; interactivity that only decorates teaches nothing — fall back to a static diagram.
   - Write it to a temporary folder (`.tmp/` under the project root, or the harness scratchpad), or publish it as an artifact where the harness supports that. It is throwaway: never commit it.

## Gotchas

- Knowledge-backed explanation is the fluency trap: it reads equally confident whether right or wrong. The attribution discipline is what separates this skill from a plausible lecture — keep it even when it feels pedantic.
- An explainer that walks the artifact section by section is a summary wearing an explainer's clothes; reorder around the idea, not the table of contents.
- The popular simplification of a concept is often itself the natural-but-wrong reading to correct — check whether the well-known version is accurate before repeating it.
- A quiz the user can pattern-match without understanding is worse than no quiz: it certifies a gap as covered.
- Depth must scale inversely with target size: a book-length artifact gets an argument-altitude explainer, not a chapter walkthrough.
- A micro-world drifts from the explained target easily; rebuild it after the understanding changes rather than trusting an old simulation.
