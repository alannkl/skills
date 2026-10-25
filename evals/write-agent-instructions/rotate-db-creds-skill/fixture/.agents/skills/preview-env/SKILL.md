---
name: preview-env
description: Spin up or tear down a preview environment for a branch of the orders service. Use when asked for a preview env, a review app, or to test a branch in the cluster.
---

# Preview environments

Preview envs live in the `preview-<branch>` namespace on the staging cluster.

1. `kubectl config use-context staging`
2. Create: `./scripts/preview.sh up <branch>`; it prints the URL when ready.
3. Tear down: `./scripts/preview.sh down <branch>`.

Never create previews on the prod context.
