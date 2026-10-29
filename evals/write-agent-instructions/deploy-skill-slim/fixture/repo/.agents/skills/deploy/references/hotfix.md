# Hotfix deploys

Use when the user calls the deploy a hotfix.

- Skip the canary, including in production.
- Still run the health gate (step 5 of SKILL.md).
- After a passing gate, tag the commit: `git tag hotfix-<YYYY-MM-DD> <sha> && git push origin hotfix-<YYYY-MM-DD>`.
