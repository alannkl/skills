# Billing portal plan

## Milestones

1. API on the new invoices schema — done
2. Portal pages for invoices and payment methods — done
3. End-to-end suite (Playwright) against the test stack — not started
4. CI: run unit and e2e suites on every PR — not started

## Decisions

| ID | Decision | Status | Blocks |
| --- | --- | --- | --- |
| D160 | Invoices schema uses integer cents | decided | |
| D161 | Portal is server-rendered with htmx, no SPA | decided | |
| D162 | Stripe webhooks verified with the signing secret, retried by Stripe | decided | |
| D163 | Payment methods listed from Stripe on each page load, not cached | decided | |
| D164 | Use Playwright for the e2e suite | decided | |
| D165 | The test stack runs Postgres, the API and stripe-mock in docker compose | decided | |
| D166 | E2E tests run against stripe-mock, never Stripe test mode | decided | |
| D167 | Test data: SQL fixture loaded at stack start, or seeded through the API per test | open | milestone 3 |
| D168 | Playwright runs Chromium only until the suite is stable | decided | |
| D169 | CI runner size for the e2e job | open | milestone 4 |
| D170 | E2E login: seeded test user with a known password, or a test-only magic-link endpoint | open | milestone 3 |
| D171 | Invoice PDFs rendered server-side with the same templates as email | decided | |
| D172 | Retry failed e2e tests once in CI, never locally | decided | |
