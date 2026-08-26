# Cheap Code, Expensive Systems

On adversarial review, review triage, and the costs we forget to define when agents write the code.

## Background: the loop

A pattern that works well in agentic coding: an author agent produces a solution, an adversarial reviewer attacks it, the author triages the findings, accepted problems get fixed, and a verifier confirms the fixes landed. Frontier models already self-check while writing, but an explicit adversarial pass still earns its place. A fresh context with the single job of breaking the solution finds things the authoring context cannot, because the reasoning that produced a bug tends to defend it.

The loop has a known failure mode, and it is not that the reviewer misses things. It is the opposite.

## The problem: a prompted skeptic always finds something

Ask a model to attack a piece of code and it will comply. Every time. It can always produce more edge cases, a cleaner abstraction, a hypothetical future requirement, one more theoretical failure mode. Few of these findings are wrong, exactly, and that is what makes them dangerous. If every valid finding gets fixed, the review loop becomes an over-engineering machine. Each cycle adds guards, flags, abstractions, and special cases, and the system grows steadily more expensive to own while becoming no more correct.

So the workflow needs a stopping rule, and the stopping rule rests on a single principle:

> **A finding can be valid without being worth fixing.**

Everything else in this piece is machinery for applying that sentence without turning it into an excuse to ignore real problems.

## Diagnosis: over-engineering is an undefined-cost problem

Why do agents over-fix? Two causes compound.

The first is that we hand agents incomplete objective functions. "Fix all reviewer findings" prices every fix at positive value, because nothing in the instruction says that architectural complexity, cognitive load, operational burden, coupling, new failure modes, and long-term change cost are costs. Humans carry those prices implicitly and assume they are obvious. The agent optimizes exactly what was specified, and what was specified is a benefit column with no cost column. Agents do not naturally over-engineer; they optimize against the costs we forgot to specify.

The second is training bias. In the text models learn from, handling more edge cases reads as quality, extra safeguards read as diligence, and thoroughness gets rewarded. So even a well-specified cost model decays under pressure. The agent drifts back toward completeness unless the cost model sits at a point in the workflow where it decides an actual outcome, rather than in a preamble the agent reads once and forgets.

Both causes point at the same repair: define the costs, then enforce them where decisions get made.

## The cost model: what actually costs something

The prices in an agentic workflow are not the prices human intuition was trained on. Ranked from cheapest to most expensive:

| Resource            | Price             | Consequence                                                                                                         |
| ------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------- |
| generated code      | ~free             | Never preserve undeployed code because rewriting "looks like work". Diff size is not a cost.                        |
| re-verification     | cheap, not free   | Each review cycle costs wall clock and finds different things. Batch fixes so one pass covers them; cap the cycles. |
| human attention     | expensive         | Spend it on decisions and escalations, never on raw diffs and finding lists.                                        |
| deployed complexity | compounds forever | Every state, flag, special case, dependency, and failure mode is paid for over the system's whole life.             |

For greenfield code the consequences are blunt. Lines of code, number of files touched, amount rewritten, size of the diff: none of these are costs before deployment. A full rewrite of undeployed code can be cheaper than a small patch when the rewrite yields a simpler system. "Minimum sufficient fix" never meant minimum code change. It means the minimum total complexity required to make the system correct.

Human instinct gets this backwards. We price a rewrite as expensive because it looks like a lot of work, and a small patch as cheap because it looks small. For an agent, generating five hundred fresh lines instead of patching fifty costs nothing worth counting. What is not free is the special case the fifty-line patch leaves behind, which every future reader and every future change now pays for.

One caveat keeps the rule honest. A rewrite discards the artifact's verification state: the review that just happened applies to the old code, and the new code needs its own pass. Re-verification is cheap in an agentic workflow, but it is not free. So the honest form of the rule is that a rewrite must be worth at least one extra review cycle. For a genuinely simpler design, it almost always is.

### Two kinds of cost, two ways to transmit them

Some costs are declarable facts, and stating them changes agent behavior immediately. This service is pre-deployment and its database is throwaway, so migrations have zero value. This module has one caller. This process restarts for free. Write facts like these down where the agent will read them. Without the first one, any competent agent writes migration-safe code, because migration safety pattern-matches to quality; with it, the behavior flips, because migration-safe code for a database with no data is pure waste.

Other costs are judgments. "Too much abstraction", "cognitive load", "lifecycle complexity" cannot be written as terms in an objective function; every attempt collapses into either a slogan the agent nods at or a metric it games. Asking the agent to run a six-point cost evaluation before every change fails the same way, producing plausible cost analyses that justify whatever it was going to do anyway. Judgment costs transmit the only way taste ever has: worked examples, persisted corrections, and review of the agent's dispositions rather than its arithmetic.

Specify what you can declare. Demonstrate what you can only judge.

## Triage: findings are inputs, not instructions

Reviewer output is evidence for a decision, not a work queue. The author makes that decision. Not because the author is neutral, but because the author holds the context: the hidden constraints, the deliberate trade-offs, the reasons the code is shaped the way it is. A reviewer without that context has a high false-positive rate by construction.

That context asymmetry is real, and it cuts both ways. The author is also the least independent party available, and in agent workflows the problem sharpens: a model triaging findings against its own output will often reproduce, as a rationalization, the same reasoning that produced the bug. Two mechanisms keep author-led triage honest.

**Move context to the reviewer, not triage away from the author.** The author emits a short review brief beside the code: intent, the requirements it satisfies, deliberate trade-offs, known limitations, declared non-goals. The reviewer reads it before attacking. This kills a whole class of invalid findings before they are written, and it makes rejections auditable. "Declared trade-off #2" is a checkable rejection; "I had my reasons" is not.

**Make both sides carry evidence.** Every blocking finding states a concrete failure scenario: these inputs, this state, this wrong outcome. Every rejection states the specific reason the scenario cannot occur: the guard clause at a line, the test that was run, the constraint in the brief. This converts triage from opinion against opinion into claims someone can check. Rejections are never free.

Each finding then passes through a gate before any matrix: is it valid at all? Then materiality, then the cost of the fix. Five dispositions come out the other side. Fix, defer, and reject are the agent's to take alone. The other two, redesign and clarify-the-requirement, are escalations, because reshaping the system or changing what it is supposed to do belongs to the human.

## High impact, high cost: the cost of a fix is measurement data

When a finding is real, material, and expensive to fix, do not patch by default. The expense itself is a reading on the design. Cheap fixes confirm a design; expensive fixes indict it. A correct requirement that the architecture makes painful to satisfy is the architecture telling you it is fighting the problem instead of fitting it.

Agents underestimate the lifecycle cost of their own patches, so do not ask for an abstract estimate. Look for concrete tells that a proposed fix is expensive:

- it adds a new state, flag, or failure mode
- it adds a special case to a previously uniform rule
- it needs coordinated changes across module boundaries
- its explanation needs "except when" or "unless"
- it suppresses the symptom without explaining why the design allowed it

Two or more tells route the finding to reconsideration instead of a patch:

```text
High-impact finding, and the proposed fix is expensive
        |
        v
Why is it expensive?
  architecture mismatch | misunderstood requirement
  invalid assumption    | inherent domain complexity
        |
        v
Compare, once:
  A. Patch the current design
  B. Redesign the affected area
  C. Clarify or change the requirement
        |
        v
Choose the lowest-total-cost correct system,
with a recommendation
```

The fourth diagnosis, inherent domain complexity, is the escape hatch that keeps the rule from thrashing. Some expense is just the domain. A process that crashed mid-flight can never be proven dead, and no redesign makes that simpler; the retry logic it forces is a cost you pay, not a smell you refactor away. "The domain is like this; pay the cost" must be a legitimate, non-shameful outcome of reconsideration, or root-cause analysis degenerates into a perpetual redesign loop.

Two guards complete the rule. The fork is one-shot: options compared once, a decision made, the loop commits, and the design is not re-litigated next cycle. And the fork is the workflow's natural escalation gate. Of everything the loop produces, "here is the finding, here is why the patch is expensive, here are the three options and my recommendation" is the message most worth a human's attention.

## Stopping rules must be structural

Cheap re-verification removes the natural economic brake on the loop. Nothing stops review, fix, review from cycling forever, and because reviewers are non-deterministic, each fresh pass finds different things. No agent in the loop will volunteer to stop, so the workflow has to stop mechanically:

- a hard cycle cap, low, on review rounds
- every review after the first scoped to the delta of the fixes, not the whole artifact
- an empty blocking list treated as an expected, rewarded outcome, so the adversarial stage is allowed to pass work
- final verification asks the closed question, "were the accepted problems resolved, and did the fixes regress the touched area", never the open one, "what else could be improved"

That last distinction is the whole game. Fixes introduce bugs at a meaningful rate, especially fixes written under the framing "make the reviewer's finding go away", so a scoped delta-check is always worth its price. A fresh open-ended critique never is, because it restarts the machine this entire framework exists to stop.

## The short version

1. A finding can be valid without being worth fixing.
2. Findings are inputs, not instructions.
3. Review for failure, not perfection. Raise the floor, don't chase the ceiling.
4. Code is nearly free. Re-verification is cheap. Attention is expensive. Deployed complexity compounds forever.
5. Before deployment, optimize for the simplest correct design, not the smallest diff.
6. Rejections need evidence, not authority.
7. An expensive important fix questions the design before it earns a patch.
8. Inherent complexity is paid, not patched away.
9. Stopping rules are structural, not economic.
10. Over-engineering is an undefined-cost problem.
