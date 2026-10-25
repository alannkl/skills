---
description: Deploy shipyard to an environment
argument-hint: <staging|prod>
---

1. Run `./scripts/deploy.sh --dry-run $ARGUMENTS` and show me the diff.
2. Ask me before deploying. Only after I say yes, run `./scripts/deploy.sh $ARGUMENTS` and report whether the rollout succeeded.
