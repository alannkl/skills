# Diagnosing Bugs

Diagnose before fixing whenever the cause is not already evident. Scale to severity: a typo-level bug needs none of this; an intermittent or high-impact defect needs all of it.

- Build the feedback loop first: the tightest available check that reproduces the symptom and can show both failure and success. If you catch yourself reading code to build a theory before this check exists, stop and build it.
- Minimize the repro until every remaining element is load-bearing; each element removed eliminates a family of causes.
- Generate 3–5 competing hypotheses before testing any — a single hypothesis anchors on the first plausible idea. Write each as a falsifiable prediction ("if X is the cause, changing Y makes the symptom disappear"), rank by likelihood, and run the cheapest discriminating probe first.
- A probe that disproves a hypothesis is progress: record the ruling-out and move to the next hypothesis rather than re-testing variations of the dead one.
- Tag every temporary log, print, or probe with one unique prefix (such as `[DBG-a4f2]`) so cleanup is a single search; remove them all before finishing.
- With the cause confirmed, return to the workflow: fix the shared cause per step 1, with the regression-test-first evidence Behavior-First Testing requires.
