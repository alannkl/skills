# Deploy checklist

We started this checklist in 2023 after the payments outage, and it has grown over several postmortems. Thanks to everyone who contributed.

Every deploy or release pull request must pass all six checks:

1. Database migrations are backward compatible with the currently deployed code.
2. Every new environment variable has a default or is set in all three environments.
3. Feature flags for new behaviour default to off.
4. The rollback steps are written in the pull request description.
5. Dashboards and alerts exist for any new endpoint.
6. The on-call engineer for the deploy window has approved the pull request.

## Kubernetes resource limits

Only relevant when the pull request changes a Kubernetes manifest.

| Service | CPU request | CPU limit | Memory request | Memory limit |
| --- | --- | --- | --- | --- |
| api | 250m | 1 | 256Mi | 1Gi |
| worker | 500m | 2 | 512Mi | 2Gi |
| web | 100m | 500m | 128Mi | 512Mi |
