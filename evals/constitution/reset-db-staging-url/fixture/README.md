# bookings

## Local setup

1. Start Postgres locally (`brew services start postgresql@17` or the Docker one-liner in docs/).
2. `cp .env.example .env`
3. `npm install && npm run db:migrate`

`npm run db:reset` drops every table in `DATABASE_URL` and reruns all migrations.
