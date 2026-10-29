# Canary deploys (production only)

1. Run `kubectl set image deploy/api-canary api=registry.internal/api:<sha> -n production` and wait for `kubectl rollout status deploy/api-canary -n production`.
2. The canary takes 5% of traffic. Run `make health ENV=production TARGET=canary`; it passes when the error rate stays under 1% and p95 latency under 400 ms for 10 minutes.
3. Only then deploy the main `deploy/api`.
4. If the canary fails, run `kubectl rollout undo deploy/api-canary -n production` and stop.
