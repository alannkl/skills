# Scale orders-worker

Bump `replicas` in `k8s/orders/overlays/<env>/worker-patch.yaml`, open a PR. Don't `kubectl scale` by hand; Argo will revert it.
