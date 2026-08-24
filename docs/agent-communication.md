# How an agent should communicate with its human

The evidence base behind the `## Communicating` section of [AGENTS.md](../AGENTS.md). That section is the gist; this doc records everything the survey found bearing on agent → human communication, ordered by how directly it applies, with sources. Surveyed: this repo's skills, the [unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) skill, the [pstack skills](https://github.com/cursor/plugins/tree/main/pstack/skills) (cursor/plugins), and [mattpocock/skills](https://github.com/mattpocock/skills).

Each theme ends with where it landed: a rule in `Communicating` (→ #n), another constitution rule, or doc-only with the reason it stayed out of the always-loaded gist.

## 1. The thesis

Communication is judged by the audience, never the author. A message is worth what the reader leaves with — their outcome: what they can now understand, decide, and do — against what it costs them: their attention. For an agent this holds without exception; writing-to-think and self-expression have no place in a reply whose only job is to transfer understanding and enable a decision. The operational test (pstack poteto-mode): name who the work is for and what changes *for them* before any implementation detail — "if you can't say what either would notice, the work or the explanation is off."

Three consequences of the frame that a looser "write for the audience" misses:

- **Value means outcome, not approval.** What the reader can correctly do or decide after reading — never how the message lands. The sycophancy trap (pstack `why/epistemics`): a user's question often embeds a hypothesis ("I assume it's for performance?") — "the user's guess is a prompt for investigation, not a conclusion to validate."
- **Cost means wording, not content.** Some substance is irreducibly hard; the promise is that no reader effort is wasted on the prose, not that hard ideas become easy. Chasing effortlessness itself produces the over-corrected telegram register and the smoothed-over report that drops its caveats — calibration to the evidence is a separate duty, owned by "Evidence over assertion".
- **The author's ego is out; the author's judgment is in.** Candid judgment, opinions, and honest confidence are content the audience needs ("a recommendation is a judgment, not a validation. Agreement is not the default; candor over sycophancy" — pstack poteto-mode). What the audience never needs is the author's convenience: sounding thorough, smart, or finished.

→ section intro.

## 2. The failure modes

The recurring ways an agent's message fails its reader, collected across the survey and beyond any one skill's framing. Each maps to where it is tackled ("#n" = a `Communicating` rule).

- **The buried lede.** The answer arrives after the process chronology, or at the end of a wall of text, so stopping early costs the reader the answer. The most-repeated concern in every source: findings before scope, outcome before session log, capsule first. → #2.
- **The pointer instead of the answer.** The reply hands the reader homework — a file path, a "you can check by…" — in place of the substance itself ("deliver the outcome section itself in chat, not a pointer to the file" — brainstorm; "remove findings that would require the author to 'check' something the reviewer can inspect" — code-review). → #2.
- **Padding.** Substance manufactured to look thorough: invented findings, filler caveats, empty template sections, follow-ups for their own sake. → #4 and #7.
- **The telegram.** Over-compression: a brevity instruction obeyed by clipping words and dropping caveats, leaving the reader less informed rather than less burdened. The [wait-what](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) insight: "be concise" names the output and over-corrects; naming the listener's state restores the missing premise — "shorter and clearer, not shorter and blunter." → #4 and #6.
- **The jargon wall.** Technically thorough and still incomprehensible — a reply can be complete, accurate, and failed. The mode pstack's [bro](https://github.com/cursor/plugins/tree/main/pstack/skills/bro) exists to repair: "stop using jargon and speak coherently… like one human talking to another." → #5, with #1.
- **Invented vocabulary.** Codenames and shorthand coined mid-work, or synonym-switching that makes the reader re-derive that two words mean one thing. → #1.
- **The ungrounded explanation.** Curse of knowledge: leaning on concepts the reader never got, detail before intuition — "it assumed I already knew things, and used terms it never defined" (the commonest live complaint in mattpocock's teach docs). → #1 and #3.
- **Slop.** AI tells and voiceless sterility: chatbot phrases, sycophantic openers, puffery, hedging stacks, how-it-feels claims in place of what-it-does. [unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) holds the full inventory plus the other half, "add soul" — opinions, varied rhythm, specificity — since sterile prose is just as obvious a tell. Its sharpest test made rule #5 directly: "if the sentence could appear unchanged in another project's docs, it says nothing about this one." → #5 carries the principle; the mechanical rules stay in the skill.
- **The validation reply.** Telling the reader what they would like to hear; confirming their embedded guess instead of investigating it. → the intro's value-means-outcome frame, plus "Push back on real issues".
- **The confident guess.** A gap filled with plausible narrative, hedges dropped to sound authoritative, success claimed without evidence — "they'll act on the guess." → "Evidence over assertion" and "Report failures faithfully" own this; #5 keeps hedges as content.
- **Repeating louder.** Answering a confusion signal by restating the same pitch, or the same pitch minus words. → #6.
- **The menu, and decision exhaustion.** Options enumerated without a recommendation; multi-paragraph questions; questions the agent could have answered itself. → #7, with "Recommend, don't enumerate" and "Before starting" #2.
- **Decoration.** Diagrams, headings, and formatting that don't beat prose — furniture spending attention on form. → #3.
- **Voice flattening.** In editing and capture tasks: paraphrasing the user's words ("paraphrasing is silent judging" — brainstorm) or smoothing their register into generic corporate prose (refine-it). Doc-only: owned by the editing skills.

## 3. Composing the message

**Order for the reader, not the work.** The most-repeated rule in the whole survey. Findings before scope (code-review); outcome before session log — "the session log is the appendix, not the argument" (brainstorm); final version first (refine-it); lead each question with the recommended answer "so the user can accept it in a word" (mattpocock setup); "lead with the capsule… deeper detail goes below or gets cut" (pstack recall); plans lead with the decisions most likely to change (grill-to-plan). → #2.

**Proportional, selective, never padded.** Summaries proportional to the change (document-code, simplify-code); "if your 'Act On' list has more than 5 items, you're probably not filtering hard enough" (pstack lead-judgment); no invented findings to avoid an empty review, no padded quiz rounds, no invented message when there are no changes (code-review, explain-code, commit-message); drop empty sections (pstack PR playbook); "when something is simple, don't pad it out" (pstack how). The counter-rule that keeps this honest: "terse is not an excuse to drop content" (poteto-mode) — caveats, trade-offs, failures, and open decisions survive every cut; shorten-it's contract is the same: cut repetition, filler, hedging, transitions — preserve claims, caveats, numbers, names. → #4.

**Ground every concept; one name per concept.** A message loses the reader the moment it leans on a concept they neither brought nor were given — and the unit is the concept, not the jargon word (mattpocock writing-shape). One canonical name, kept: "a doc that says 'the gate', 'the ratchet', and 'the budget check' for one thing teaches three things" (pstack technical-writing); "concision is not an excuse to drift" from the shared vocabulary (mattpocock HTML-REPORT); use the real symbol, file, flag, or command name, not a synonym or a description of it. Never make the reader decode labels coined mid-work. → #1.

**Concrete over abstract.** "Say 'the `UserService` calls `AuthClient.refresh()`', not 'the service delegates to the client'" (pstack how); say what it does, not how it feels — if a sentence can't be restated as a concrete instruction, fact, or number, cut it (unslop); "a single verbatim quote with a precise citation beats a paragraph of plausible-sounding summary" (pstack why); "be specific over sterile: not 'schema changes can cause issues' but 'a column rename fails the build'" (pstack technical-writing). → #5.

**Write clean on the first pass.** poteto-mode: "the cleanup-afterward pass has been measured to fail, so never generate the bad sentence in the first place." Doc-only: a mechanism, not a principle — the constitution states the target, not the drafting order.

**Plain-language mechanics** (pstack technical-writing, for when the register itself needs work): short declarative sentences, one thought each; condition before instruction; common case first; say who does what; never "simply/easy/quickly" in a procedure — "if it were simple, the reader would not be here"; keep "only" and "not" next to the word they change; make every "it/this" point at one obvious thing; headings carry the point, not just the topic. Doc-only: style-guide altitude, below the constitution's.

## 4. Honesty and epistemic register

Mostly already encoded in "Evidence over assertion" (While working #1) and "Report failures faithfully"; the survey added texture:

- Five confidence tiers with distinct phrasings — direct (cited, present tense), supported, inferred (hedged, chain explicit), speculative (marked as a guess), unknown ("one of the most valuable outputs"; be specific about what you searched) (pstack `why/epistemics`).
- Hedges are content, not style: "dropping the hedges to sound more authoritative is the exact failure mode this skill exists to prevent"; confidence words ("because", "was designed to", "fixes") need a citation immediately adjacent. Avoid "obviously", "clearly", "just".
- "Failing to mark a gap and filling it with a confident guess actively harms the user; they'll act on the guess." A report with no "what we don't know" is suspicious.
- Show what you rejected: a "Dismissed" section "is a trust mechanism… lets them override your judgment where they disagree" (pstack lead-judgment).
- Never fabricate a link, citation, or transcript reference; label inference as inference everywhere (explain-code, handoff, commit-message).
- "Treat a confident reply without evidence as a red flag"; a green build proves it compiles, not that it works (pstack guide).

→ hedge-as-content made #5; the rest lives in While working #1 and #3 of "When you disagree".

## 5. Explaining and teaching

- Background → intuition → one concrete example → details; shrink the world to a toy when the real one is too big (explain-code). → #3.
- Attack the natural-but-wrong reading; "dislodging the wrong model beats stating the right one beside it" (explain-code). → #3.
- Match altitude to the question: behavior, not file inventories; a "why does X happen" gets the trace, not a restated overview (explain-code).
- "Give the smallest complete answer first, a sentence or two, then stop. Add layers when they ask. Never a wall of text" (pstack teach). Working memory is small; put the depth where their question is, read from the conversation rather than quizzed out of them.
- No pacing theater or framing labels: don't print "the key insight", "this is the tricky part", "TL;DR" — just say it (pstack teach, mattpocock writing-docs: "the formula reads as filler").
- Diagrams only when they beat prose — "never diagram what a sentence covers" (explain-code, grill-to-plan, pstack how); for 3+ moving parts, a short series that adds one part per frame beats one all-at-once diagram (pstack teach).

→ #3 carries the spine; the rest are skill-level detail (explain-code already owns them here).

## 6. Asking the human questions

- Never ask what you could look up: "finding facts is your job; the decisions are the user's" (mattpocock grilling, grill-to-plan, poteto-mode — "a throwaway probe usually answers faster, and it hands the human a result to react to instead of a decision to make").
- Make rounds answerable by number: numbered questions, each with a marked recommendation, so the answer can be "1 yes, 2 the second option" (mattpocock grilling, explain-code's offer lists).
- "Correct me" statements beat questions: the user can't volunteer facts they don't know are in play, but correcting a wrong statement is instant (brainstorm).
- One question at a time when depth matters; don't re-ask resolved questions; if the user replies with a question instead of a decision, switch to discussion in prose — a picker is for collecting decisions, not delivering explanations (grill-to-plan).
- The live complaint to avoid: "every question is three paragraphs long… the verbosity itself causes decision exhaustion" (mattpocock wayfinder docs).

→ mostly encoded in "Before starting" #2 and "Recommend, don't enumerate"; the round/format mechanics stay skill-level.

## 7. Voice, trust, and ownership

- Don't paraphrase people: "paraphrasing is silent judging" (brainstorm); don't flatten a user's casual or opinionated register into corporate prose (refine-it). Doc-only: applies to editing tasks, which the skills own.
- Own every subagent's work: review it and write your own summary; never pass through what it said (poteto-mode).
- Redact secrets before showing anything, with markers that aid no recovery (handoff, diagnosing-bugs).
- Write logs and handoffs "the way you'd tell a teammate what you did" — a reviewer should understand each row without decoding it (pstack show-me-your-work).

## 8. Why the gist must stay short

The meta-finding that shaped how much of this went into AGENTS.md: "skills that fight verbosity fail by growing: a four-hundred-line concision skill still leaves the model verbose, because the model reads the volume, not the plea" (mattpocock wait-what docs). Same from writing-for-agents: attention thins across sprawl, and a no-op sentence — one the model already obeys by default — pays context load to say nothing. A communication section that is itself long, padded, or vague fails its own test. Hence: seven rules in the constitution, everything else here.

## Source map

| Source | Most load-bearing files |
| --- | --- |
| This repo | explain-code (+ qa/durable-home/quiz refs), refine-it, shorten-it, code-review, brainstorm, grill-to-plan, handoff, document-code, commit-message, coding-discipline, docs/working-with-agents.md |
| unslop | the 31 rules + "adding soul" |
| pstack (cursor/plugins) | poteto-mode ("Writing the reply", playbook reply contracts), bro, technical-writing, teach, why/epistemics, interrogate/lead-judgment, recall, show-me-your-work, principle-never-block-on-the-human |
| mattpocock/skills | wait-what (+ docs page), grilling, writing-for-agents, .agents/writing-docs.md, HTML-REPORT.md, teach, writing-shape/writing-beats, docs/engineering/wayfinder.md |
