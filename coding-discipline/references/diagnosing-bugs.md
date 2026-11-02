# Diagnosing Bugs

Scale to severity: a typo needs none of this; an intermittent or high-impact defect needs all of it.

- Build the feedback loop first: the tightest check that reproduces the symptom and can show both failure and success. Don't theorize from code before the loop exists.
- Minimize the repro until every remaining element is load-bearing.
- Generate 3–5 competing hypotheses before testing any, each a falsifiable prediction ("if X is the cause, changing Y removes the symptom"); rank by likelihood and run the cheapest discriminating probe first.
- Record each disproved hypothesis and move on instead of retesting variations of it.
- Tag every temporary log or probe with one unique prefix (`[DBG-a4f2]`) and remove them all before finishing.
- With the cause confirmed, fix the shared cause per step 1, with the regression-test-first evidence Behavior-First Testing requires.
