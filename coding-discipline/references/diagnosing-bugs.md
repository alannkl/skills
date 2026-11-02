# Diagnosing Bugs

Scale to severity.

- Build the feedback loop first: the tightest check that reproduces the symptom and can show both failure and success. Don't theorize before it exists.
- Minimize the repro until every element is load-bearing.
- Generate 3–5 competing, falsifiable hypotheses before testing any; run the cheapest discriminating probe first.
- Record each disproved hypothesis; don't retest variations of it.
- Tag temporary logs and probes with one unique prefix and remove them all before finishing.
- Fix the confirmed shared cause, with the regression-test-first evidence Behavior-First Testing requires.
