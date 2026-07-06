# Working with Agents

Human-facing guidance: principles for directing an AI agent to complete tasks well. Unlike the skills in this repo, which instruct the *agent*, this document is for the *user* — the person delegating, supervising, and accepting the work.

Synthesized in June–July 2026 from published guidance by Anthropic, OpenAI, Microsoft Research, Ethan Mollick (Wharton), Simon Willison, Thariq Shihipar (Anthropic), and academic human-AI collaboration research. These are high-level, provider-agnostic principles — not recipes for any specific task or tool.

These principles are operationalized as agent-side rules in the [Collaboration Constitution](../AGENTS.md), a copy-paste `CLAUDE.md`/`AGENTS.md` fragment that has the agent lead the user into following them. It also serves as this repo's live `AGENTS.md`.

## Principles

### 1. Working with agents is management, not operation

The skill has shifted from prompt engineering to delegation: explain what you need, give effective feedback, and design ways to evaluate the work. Directing an agent on a long task resembles writing a requirements doc or an SOP — the same skills that make good managers make good agent users. Treat the agent as a capable collaborator with zero context, not a vending machine: give it what you would give a new hire — intent, constraints, pointers to examples, and what "done" looks like.

### 2. State intent and success criteria, not just the task

The more precise the instruction, the fewer corrections needed. Specify scope, constraints, and especially *verifiable* acceptance criteria ("these inputs should produce these outputs") rather than just an activity ("add tests"). The nuance: vagueness is a legitimate tool when *exploring* — a deliberately open prompt surfaces things you would not think to ask. Be precise when executing, open when exploring.

### 3. Discover your unknowns — the map is not the territory

Your prompt, instructions, and context are a *map* of the work; the codebase and its real constraints are the *territory*. The gap between them is your unknowns, and every unknown the agent hits forces it to guess. Thariq Shihipar's framing sorts them into four quadrants: known knowns (what's in the prompt), known unknowns (questions you know are open), unknown knowns (tacit expectations you'd never write down but would recognize on sight), and unknown unknowns (what you haven't considered at all).

As models get stronger, quality bottlenecks on your ability to discover these unknowns, not on capability — a capable agent takes your map at face value and executes it thoroughly, so an unstated assumption fails quietly and compounds. Precision alone (#2) can't save you either: over-specify and the agent follows a flawed path past the point where it should pivot; under-specify and it defaults to generic best practices. Unaccounted unknowns make you fail both ways.

Use the agent itself to close the gap while it's cheap: ask for a "blindspot pass" over unfamiliar ground, have it teach you the domain's vocabulary, let it interview you (prioritizing questions whose answers would change the architecture), point it at reference source code instead of describing what you can't articulate, and have implementation plans lead with the decisions most likely to change. Every explainer, brainstorm, interview, and prototype is a cheap way to find out what you didn't know before it gets expensive to fix.

### 4. Separate understanding, planning, and execution

Explore first, plan second, implement third. Letting an agent jump straight to doing tends to produce a competent solution to the wrong problem, and reviewing a plan is far cheaper than reviewing a finished implementation. Scale this to risk: for a trivially small, well-understood task, planning is overhead — skip it.

### 5. Give the agent a way to verify its own work

Possibly the single highest-leverage principle. Without an objective check (a test, a build, a comparison, a measurable criterion), "looks done" is the agent's only signal and *you* become the verification loop, catching every mistake manually. Give it a check it can run and read, and it iterates until the check passes — Willison calls this "tethering the AI to reality." Related: demand **evidence, not assertions** — the actual test output, the command and its result — because reviewing evidence is faster and more reliable than trusting a claim of success.

### 6. Calibrate autonomy to risk and reversibility

Rate each action the agent can take by reversibility, blast radius, and stakes; require human approval for the irreversible or high-stakes ones; let routine work flow. Start with tight oversight and *earn* autonomy through observed reliability rather than granting it up front. Sandboxing — running agents where total failure causes limited damage — is the structural version of this principle.

### 7. Course-correct early; restart rather than argue

Tight feedback loops beat long autonomous runs inspected only at the end — interrupt as soon as you see drift. And a widely replicated failure mode: repeated correction pollutes the working context with failed approaches. After roughly two failed corrections on the same issue, stop, reset, and write a *better initial prompt* incorporating what you learned. A clean start with a refined ask almost always beats an accumulated argument.

### 8. Treat the agent's attention (context) as a scarce resource

Agent performance degrades as its working context fills with irrelevant material. Practical universals: one task per session, reset between unrelated tasks, keep standing instructions short and high-signal (a bloated instruction file gets *ignored*, not followed), and delegate bulk research to subprocesses that report back summaries. Anthropic's framing: find the smallest set of high-signal tokens that produces the outcome.

### 9. Independent review — don't let the worker grade itself

An agent (like a human) is biased toward the work it just produced. Use fresh eyes for evaluation: a separate reviewer session or agent that sees only the result and the criteria, writer/reviewer splits, or adversarial review against the original plan. Caveat: a reviewer asked to find problems *will* find some even in sound work — scope it to gaps affecting correctness and requirements, or you will over-engineer.

### 10. Preserve reversibility and legibility of the agent's work

Have agents work in ways that are easy to undo and easy to audit: incremental commits, checkpoints, progress notes. This converts mistakes from disasters into cheap rollbacks and lets you (or a future agent) reconstruct what happened. It also enables a productive working style: try the risky approach, revert if it fails.

### 11. Maintain your own understanding — calibrated, not blind, trust

Know what the system can do and *how well* it can do it (the opening guidelines of Microsoft's HAX research). A key skill is developing intuition for when you must review closely and when you don't — but shipping unreviewed output to collaborators is an anti-pattern; you remain accountable for what you ship. Review depth should scale with stakes, not with convenience.

### 12. Invest in the environment; feedback should compound

A correction given once in conversation evaporates; encoded into persistent conventions, checks, tools, and reusable workflows (such as skills), it improves every future session. Agent effectiveness is substantially an *environment* problem: good tools, good docs, good guardrails, written specs. Time spent making the spec and environment precise pays off more than time spent watching the execution.

### 13. Iterate on your own practice

These are starting points, not laws. Notice what you did when output was great, diagnose why when it wasn't (context too noisy? prompt too vague? task too big?), and keep recalibrating as capabilities shift — "assume this is the worst AI you will ever use."

**In one sentence:** be precise about intent and success criteria, discover your unknowns while they are cheap, make verification objective and independent, scale oversight to risk, keep feedback loops tight and contexts clean, and stay the accountable owner of the result.

## How these principles map to skills in this repo

| Principle | Agent-side embodiment |
| --- | --- |
| #2 intent and success criteria, #3 discover unknowns, #4 plan before executing | [`grill-to-plan`](../grill-to-plan/SKILL.md) |
| #4 scoped execution, #6 risk-scaled process, #10 legible work | [`coding-discipline`](../coding-discipline/SKILL.md) |
| #9 independent review | [`code-review`](../code-review/SKILL.md) |
| #5 evidence over assertion | Not yet embodied — candidate future skill: make the agent always show the check it ran (test output, command + result) instead of claiming success |
| #11 maintain your own understanding | Partially embodied by [`document-code`](../document-code/SKILL.md), which makes the code itself durably understandable. The session-level half is a candidate future skill, `explain-change` ([design spec](grill-to-plan/2026-07-06-post-implementation-understanding-skill.md)): an explainer plus quiz that verifies the user understands the change before merging (Shihipar), with a shareable buy-in variant — walking reviewers through the same unknowns the author started with — deferred until a real team-sharing need appears |

## Source attribution

- **Anthropic** — strongest on the operational loop: explore/plan/execute, closed-loop verification, course-correction, context management, adversarial review.
  [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) · [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- **OpenAI** — strongest on risk-tiered autonomy and human-in-the-loop approval gates.
  [A practical guide to building agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) · [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- **Microsoft Research** — 18 guidelines for human-AI interaction synthesizing 20 years of HCI research; grounds expectation-setting and calibrated trust.
  [Guidelines for Human-AI Interaction (HAX Toolkit)](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/)
- **Ethan Mollick (Wharton)** — the delegation/management framing and co-intelligence principles.
  [Management as AI superpower](https://www.oneusefulthing.org/p/management-as-ai-superpower) · *Co-Intelligence* (2024)
- **Simon Willison** — sandboxing, verification as reality-tether, calibrated trust, review anti-patterns.
  [Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/)
- **Thariq Shihipar (Anthropic, Claude Code team)** — the unknowns framing: map-vs-territory, the four quadrants of unknowns, and cheap discovery techniques (blindspot pass, interviews, references, revision-ordered plans, implementation notes, pre-merge quizzes).
  [A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/article/2073100352921215386) · [companion example artifacts](https://thariqs.github.io/html-effectiveness/unknowns/)
- **Academic human-AI collaboration research** — collaboration outperforms pure delegation when both sides model each other and feedback is continuous.
  [Collaborative Gym (arXiv 2412.15701)](https://arxiv.org/pdf/2412.15701)
