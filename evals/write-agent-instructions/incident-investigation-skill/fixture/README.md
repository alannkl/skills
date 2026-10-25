# orders-api

Order and payment backend for the storefront. TypeScript on Node 22, PostgreSQL on RDS, deployed to ECS Fargate in `eu-west-1`.

- `npm run dev`: run locally against the docker-compose database
- `npm test`: unit and integration tests
- Deploys go out from `main` through GitHub Actions; see `.github/workflows/deploy.yml`.

Production logs go to CloudWatch log group `/ecs/orders-api` (JSON lines, one per request, with `requestId`, `orderId`, `level`, `msg`). Alerts post to Slack `#orders-alerts`.

Use `scripts/db-ro.sh` for any production query; it connects to the read replica with a read-only role.
