---
name: grill-to-plan
description: Turn casual ideas, vague goals, plans, or designs into clearer decisions through scoped questioning, decision-tree review, and optional records. Use when the user wants casual idea clarification, to get grilled on a plan, to refine requirements, to update project glossary terms, to create ADRs, or to keep a session decision log.
---

# Grill to Plan

Turn a vague goal, rough idea, plan, or design into shared understanding, clear decisions, and a final actionable plan. Start with the `grill-me` behavior: ask one question at a time, provide a recommended answer, walk the decision tree branch by branch, and inspect the codebase instead of asking when the answer is discoverable.

## Modes

- Lightweight mode: use for casual ideas, early thinking, or quick clarification. Ask only the highest-value questions, keep the tone conversational, and skip repo docs unless the user asks or a durable project decision emerges.
- Documented mode: use for serious product, domain, or architecture decisions. Apply the full workflow: code/doc checks, glossary updates, ADRs when warranted, session records, and final synthesis.

## Workflow

1. Restate the goal.
   - Rephrase the user's current intent in specific, concrete terms.
   - Treat the input as a goal description until the user has provided enough decisions for it to count as a plan.
   - Say what you believe the desired end state is, what is in scope, and what may be out of scope.
   - If the initial context is too thin to make a reasonable guess, ask for the missing context first.
   - Match the ceremony to the stakes: default to lightweight mode for casual clarification and documented mode when project knowledge, architecture, or durable decisions are involved.
   - If you cannot confidently choose a mode from the initial input, ask whether the user wants lightweight clarification or documented decision capture before continuing.

2. Scope before drilling down.
   - Estimate the rough number of questions needed from the initial input.
   - If the session would need more than a handful of questions, usually around 5-7, ask scoping questions first to narrow the target.
   - Ask scoping questions in convergence order: highest-leverage boundary questions first, then progressively narrower ones.
   - Once scope is clear, switch to decision-tree order and resolve dependent decisions branch by branch.

3. Use available context before asking.
   - Do not ask questions whose answers are obvious or easily discoverable in the codebase, docs, issue tracker, or existing session log.
   - If a question can be answered by exploration, inspect the relevant source first and report what you found.
   - Look for `CONTEXT-MAP.md`, `CONTEXT.md`, and `docs/adr/` when the discussion touches domain language or architecture.

4. Ask one question at a time.
   - Begin each question by restating the current understanding of the user's goal and the relevant settled decisions.
   - Ask a non-obvious, in-depth question that moves the plan toward resolution.
   - When domain relationships are being discussed, use concrete scenarios that probe edge cases and force precise boundaries between concepts.
   - Provide your recommended answer and the reasoning behind it.
   - Use the agent's built-in ask-question tool when one is available and appropriate.
   - Keep a reasonable maximum question budget. If the budget is running long, summarize the remaining branches and ask the user which branch to continue.

5. Resolve each question before moving on.
   - If the user wants discussion, stay on that question until there is a conclusion, explicit deferral, or a documented disagreement.
   - Do not skip to the next question while the current decision is still open.
   - Before asking the next question, review the current conversation and the latest session record, then align the next question with what has already been decided.

6. Push back on weak or harmful choices.
   - If the user's proposed decision appears wrong, risky, inconsistent, or inferior to an available alternative, do not silently comply.
   - Explain why the current or alternative approach is better.
   - State the concrete downside of the proposed choice.
   - Ask whether the user wants to discuss or proceed anyway.
   - Continue only after the user confirms or gives a convincing counterargument.
   - Record the final decision. If the decision is hard to reverse, surprising without context, and based on a real trade-off, create an ADR.

7. Maintain project knowledge in documented mode.
   - Challenge terms that conflict with `CONTEXT.md`.
   - Sharpen vague or overloaded terms into precise canonical language.
   - Cross-check user claims against code when possible and surface contradictions.
   - Update `CONTEXT.md` inline when a domain term is resolved. Keep it as a glossary only, without implementation details.
   - Create `CONTEXT.md` or `docs/adr/` lazily, only when there is something concrete to write.
   - In lightweight mode, do this only when the user asks or a durable project decision emerges.

8. Maintain a session record when useful.
   - Create or update a session document as decisions crystallize. Store it at `docs/grill-to-plan/{yyyy-mm-dd}-{slug}.md` unless the repo has an established planning or decision-log location.
   - For each question, record: context, question, discussion or debate summary, final conclusion, and any follow-up.
   - Treat the live conversation as the immediate source of truth and the session record as the durable checkpoint for settled state.
   - Keep it concise enough to guide the next question without becoming a transcript.
   - Use `references/SESSION-RECORD-FORMAT.md` when creating or updating this document.
   - Skip the session record for lightweight mode unless requested or the discussion produces decisions worth preserving.

9. Finish with a synthesis sized to the mode.
   - Provide the resolved plan or clarified decision.
   - List open questions or explicit deferrals.
   - List decisions made.
   - List docs updated, including `CONTEXT.md`, ADRs, and the session record, or say none were needed.
   - List key risks or watchpoints.
   - Provide concrete next steps.

## ADR Rule

Offer or create an ADR only when all three are true:

- Hard to reverse: changing the decision later would be meaningfully costly.
- Surprising without context: a future reader would reasonably ask why this choice was made.
- Real trade-off: there were genuine alternatives and the decision chose one for specific reasons.

Use `references/ADR-FORMAT.md` when creating ADRs. Use `references/CONTEXT-FORMAT.md` when creating or updating `CONTEXT.md`.

## Gotchas

- Do not treat scoping order and decision-tree order as the same thing.
- Do not ask broad discovery questions after scope is already clear.
- Treat the question budget as a maximum, not a quota; stop asking once the plan is clear.
- Do not turn `CONTEXT.md` into a spec, roadmap, scratch pad, or implementation note.
- Do not batch resolved glossary updates until the end.
- Do not present the final plan as settled when unresolved decisions remain.
