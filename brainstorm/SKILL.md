---
name: brainstorm
description: Host a structured brainstorming session as both facilitator and participant, guiding the user from problem framing through divergent ideation to evaluation and an actionable shortlist.
disable-model-invocation: true
---

# Brainstorm

Run a facilitated brainstorming session with the user, playing two roles at once:

- **Facilitator** — own the process: phases, turn-taking, capturing ideas, protecting the rules.
- **Participant** — contribute ideas, but rationed. You are the designated wildcard, never the dominant voice.

The core risk is anchoring: you can generate 20 polished ideas instantly, and the moment the user sees them they stop surfacing their own. Every rule below that limits your output exists for that reason.

## Session state file

Create an idea-board markdown file at `docs/brainstorm/<topic-slug>.md` under the working directory (creating the directory if needed), or in the scratchpad directory when the working directory is unsuitable (read-only, or not a project this file belongs in). For a deep dive, create it at session start; for a quick spark, only once the session outgrows the chat or the user asks. Maintain it throughout: a `Phase:` line in the header, updated at every phase gate — it is what makes resuming possible — then the HMW statement and constraints, then every idea **verbatim**, tagged `[user]` or `[agent]`. A long or rambling contribution may get a short label for scannability, but keep the verbatim words under it (paraphrasing is silent judging).

## Asking structured questions

Wherever this skill says "offer a structured choice," use the harness's multiple-choice question tool (AskUserQuestion in Claude Code; other harnesses may name it differently). If none exists, present a short numbered list in plain text with your recommended option marked, and wait for the reply. Always give a recommendation with its reasoning in the option description.

## Phase 0 — Preset

Two session shapes:

- **Quick spark** — minimal framing (one confirmation question), rapid-fire ideation, light shortlist. For small, well-bounded topics (naming, a single decision, a short list of options).
- **Deep dive** — full protocol below. For open-ended, fuzzy, or high-stakes topics.

Determine the preset from the topic first; ask only when you can't:

- **Infer quick spark** when the topic is narrow and concrete with an obvious output shape ("name this module", "taglines for the launch email", "3 options for the error copy").
- **Infer deep dive** when the topic is broad, strategic, or fuzzy ("how to grow retention", "what should our Q4 focus be"), or the user signals stakes or thoroughness.
- **Honor explicit signals** over inference: "quick", "just a few ideas", "let's go deep", or a stated session length.
- **Announce an inferred choice** in one line with a cheap override ("Treating this as a quick spark — say 'deep dive' for the full session.") and proceed; reserve a structured choice for genuine ambiguity — no signals either way.

Scale every later phase to the preset. In a quick spark, Phase 2's turn discipline and judgment suspension survive intact; the rest of the ceremony drops — no idea file unless the session outgrows the chat, no clustering or stress-test, convergence in a single structured choice, shortlist delivered in chat. If mid-session the preset proves wrong (a "quick" topic keeps unfolding), offer the upgrade rather than silently switching.

## Phase 1 — Frame

Goal: a confirmed **How Might We (HMW) statement** — the problem reframed as an open question that invites solutions (e.g. "How might we make onboarding feel finished in under a minute?") — plus known constraints, written at the top of the idea file. Answer what you can from available context before spending questions on it — prior idea files in `docs/brainstorm/`, ADRs, repo docs: "already tried or ruled out" is often already recorded. Framing is a gate, not a phase to savor — 3–5 questions maximum, fewer if the topic is already sharp; if still fuzzy at the cap, start ideating anyway and re-frame mid-session rather than asking more. Batch questions into structured choices where possible (reacting to options is less fatiguing than composing answers, and a wrong option provokes the useful correction).

Dig for, in priority order:

1. **The problem behind the problem.** Users often bring a solution in disguise. One or two "why" hops upstream; _offer_ the reframe as a choice, never force it.
2. **Success criteria, including the convergence endpoint.** What does a great outcome look like — 3 directions, 30 raw ideas, one decision? And how far should convergence go: a single pick, a ranked shortlist, or only a filtered candidate list the user will take to their team?
3. **Real vs. assumed constraints.** Ask which constraints are actually hard. Record the assumed ones — they are provocation ammunition for Phase 2.
4. **Already tried or ruled out.** Avoids proposing rejected ideas.

**State your silent defaults before confirming the frame** — as a "correct me" statement, not questions. For a designed artifact: platform/medium, audience, where and when it's used ("I'll assume: mobile app, used on-the-go, consumer audience — flag anything wrong"). The user can't volunteer facts they don't know are in play, but correcting a wrong statement is instant. Record the corrections and surviving assumptions in the constraints block.

Confirm the final HMW statement before moving on. Mid-session reframing is allowed and cheap: if ideation keeps drifting from the frame, ask whether the frame is wrong rather than policing the drift.

## Phase 2 — Diverge

Judgment is suspended. State the rules once at the start: quantity over quality, wild ideas welcome, building on ideas encouraged, evaluation comes later. Judgment includes your own reflexes — no ranking, no praise ("great idea"), no feasibility caveats ("that might be hard because…"); park the urge for Phase 3 the way a facilitator deflects a participant's.

Turn discipline:

- **User goes first, always.** Open each round by eliciting the user's ideas before contributing yours.
- **User ideas arrive as free text — never as multiple choice.** Options are anchors by construction. The one legitimate structured choice in this phase is process direction (e.g. "next: a constraint, a reversal, or an analogy prompt?").
- **Ration your contributions: 1–3 ideas per turn.** At least one must build on a user idea ("yes, and") rather than open a fresh direction.
- **Rhythm: build twice, stretch once.** Building validates; stretching (inverting the user's direction, opposite-extreme ideas) expands the space. Stretching every turn reads as contrarian.
- **Adapt the ration to the user's mode.** Some users generate; most mostly react — curating, questioning, challenging feasibility. Still open elicit-first: the first round tells you which user you have, and a batch-first opening would anchor a generator into reacting. Flip fast — after one reacting round, or immediately on an explicit signal ("you generate, I'll pick"): offer slightly larger batches (3–5 ideas, still never a wall) to curate, and treat their reactions, questions, and challenges as contributions — capture them on the board and build on them. In this mode provocations carry more of the rhythm and may come more often — they do the generative work the user isn't. Keep inviting their own ideas at natural openings, without nagging.
- **Wildcard duty:** every few turns contribute one deliberately impractical idea, labeled as such. You bear the social cost of absurdity so the user doesn't have to.
- **Declare presuppositions.** When one of your ideas rests on context not in the frame (platform, medium, audience situation), name it the first time it ships ("this assumes mobile") and add it to the assumed-constraints list. Undeclared premises propagate through every build-on, and the sacred-cow provocation can only attack recorded assumptions.

Let the obvious ideas empty out — they always come first and that's fine. When the flow slows (short answers, repetition), do NOT end the phase: this is where original ideas start. Lulls are per-direction, not only session-wide — when one thread empties while the session still has energy, provoke or redirect at that local dead end rather than waiting for the whole session to sag. Inject a **provocation**:

- **Artificial constraints:** zero budget; ship in a week; 10× users tomorrow; must work offline.
- **Reversal:** "How would we make this problem as bad as possible?" — then invert the answers.
- **Role/analogy:** "How would a game studio / hospital / Amazon solve this?"
- **Sacred cow:** attack an assumed constraint recorded in Phase 1 ("you said it must be a mobile app — what if it weren't?").
- **SCAMPER** on an existing idea: Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse.

**Seeding a provocation:** you may answer your own provocation with exactly **one** example to set the register (especially permission-to-be-silly), then hand the floor to the user. One seed primes; several answers anchor.

After a provocation round or two past the lull, offer the phase gate as a structured choice: another provocation round, or move to evaluation. Recommend based on energy.

## Phase 3 — Converge

Announce the shift explicitly: "Divergence is over — judgment is now allowed." Never mix the modes.

Converge only as far as the Phase 1 endpoint asks. When the real decision happens elsewhere (with a team, later), ruling out the weak and irrelevant and stopping at a solid candidate list is a complete convergence — don't push for a single winner nobody requested.

1. **Cluster** the ideas into named themes in the idea file.
2. **Rank with stated criteria** (the Phase 1 success criteria, plus impact and novelty where they fit the topic — a naming session cares about fit and memorability, not impact) — never popularity or safety. **Protect one wildcard slot** in the shortlist for the boldest idea, even if it scores lower; consensus ranking systematically kills novel ideas.
3. **Stress-test the top 3–5:** for each, state what would have to be true for it to work, the biggest risk, and a cheap way to test it. Contribute your own answers here — this phase plays to your analytical strengths.
4. **Make the candidates judgeable.** When shortlisted ideas are hard to compare in prose — UI flows, visual layouts, names or copy in context, API shapes — offer to render the top candidates cheaply (throwaway mockups, clickable prototypes, sample snippets) before any final decision, using the harness's prototyping tools or skills when available. For UI topics especially, treat mockups as a prerequisite to deciding, not a follow-up. A rendering's framing choices (device, form factor, medium) are decisions to confirm with the user, not defaults to inherit.
5. **Decide via structured choices.** Present clusters to develop (multi-select) and, when the goal includes a final pick, single-select choices with trade-offs in the descriptions. Recommend, with reasoning — but sparingly: if you rank the ideas _and_ pre-select every winner, you've become the backseat driver. The final call must feel, and be, the user's.

## Phase 4 — Output

Finalize the idea file as a shareable deliverable, restructured **outcome first**: at the top, the session outcome — the final decision or the surviving candidate list, whichever the Phase 1 endpoint produced — with **next steps with owners** (an idea without an owner and a next action dies within a week). The outcome section must stand alone: the decision carries its why, and each candidate a short case — why it survived and its main risk or limitation, drawn from the stress-test notes — so a teammate who wasn't in the session can discuss and decide from it without reading further. Below that: HMW + constraints, clusters, shortlist with stress-test notes, and the full idea board last — the session log is the appendix, not the argument.

Keep it all in this one file — a standing separate deliverable drifts out of sync the moment the session reopens. If the user wants a log-free version to share, generate it on request as a disposable export of the top sections; the session record stays the single source of truth. Close by delivering the outcome section itself in chat — the decision or candidates with their cases, not a pointer to the file — then say where the file is.

## Out-of-phase input

Phase discipline binds you, not the user — they can add anything at any point. Never tell the user to hold a thought for later; accept it and route it:

- **New context or constraints, any phase** ("oh, I forgot — the budget is fixed"): update the frame and constraints block in the idea file, flag which existing ideas it affects — mark them, don't delete them — and resume the current phase. If it changes the topic materially, offer a reframe.
- **New ideas during convergence:** welcome them — late ideas sparked by seeing the whole board are often the best of the session. Capture on the board as usual, slot into an existing or new cluster, include in the ranking. If several arrive in a row, offer a short return to divergence instead of evaluating each one on arrival.
- **Judgment requests during divergence** ("is that a good idea?", "just pick the best one"): the explicit request overrides the judgment ban, but treat it as a phase-gate signal — offer the choice of a quick verdict then back to diverging, or moving to convergence now.
- **Wrap-up signals, any phase** ("that's enough, wrap it up"): don't offer another round — jump to convergence scaled way down (a quick cluster-and-shortlist, or straight to Phase 4 if they just want the board saved), and finalize the file as usual.

## Gotchas

- **User opens with a flood of their own ideas** (a pasted list, 15 ideas in one message): don't restart the protocol from Phase 0 as if they hadn't spoken. Capture the list verbatim, infer the preset and a draft frame from it, confirm the frame in one question, and enter Phase 2 already building on their material.
- **User explicitly asks you to generate a batch** ("give me 20 taglines"): the ration is an anti-anchoring default for co-ideation, not a veto over a direct request — deliver the full batch. Then invite reactions and additions and return to the normal rhythm; their curation of your batch counts as their contribution.
- **User says "you go first" or contributes nothing when invited:** the user-goes-first rule is anti-anchoring, not a deadlock. Contribute one small, deliberately rough batch (2–3 ideas, at least one bad on purpose) to lower the bar, then hand back.
- **An idea file for this topic already exists in `docs/brainstorm/`** (resumed or repeated session): read it and offer to continue from its current phase rather than starting over or silently overwriting it.
