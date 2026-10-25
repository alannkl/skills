# AGENTS.md

Platform repo: k8s manifests, Terraform, and runbooks for the orders stack.

- `k8s/` — Kustomize bases + overlays (`staging`, `prod`)
- `terraform/` — AWS infra (don't `apply` from an agent session; open a PR)
- `ops/runbooks/` — human runbooks

Never print secret values into the chat or logs. Use `kubectl get secret ... -o name` to check existence, not `-o yaml`.
