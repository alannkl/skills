# member-portal

Members' account pages: profile, avatar, billing details.

Runs on ECS in eu-west-1 (`deploy/service.yaml`); scaled to 2 tasks on 2026-10-14 for the autumn campaign.

```
DATABASE_URL=postgres://localhost/portal npm start
```
