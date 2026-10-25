# 2026-07-14 Stripe webhook timeouts

**On call:** Priya. **Status:** resolved.

At 09:12 UTC `#orders-alerts` fired "p95 latency > 2s on POST /webhooks/stripe". Priya started by tailing the logs:

```
aws logs tail /ecs/orders-api --since 30m --filter-pattern '{ $.path = "/webhooks/stripe" && $.durationMs > 2000 }' --format short
```

Most slow requests were waiting on the `orders` table lock. Logs Insights made the pattern clear:

```
aws logs start-query --log-group-name /ecs/orders-api \
  --start-time $(date -d '-1 hour' +%s) --end-time $(date +%s) \
  --query-string 'fields @timestamp, requestId, orderId, durationMs | filter path = "/webhooks/stripe" | sort durationMs desc | limit 50'
aws logs get-query-results --query-id <id from start-query>
```

The slowest request was `req_8f2c1e` on order `ord_55120`. Checked what was holding locks on the replica's primary metrics, then on the DB itself:

```
scripts/db-ro.sh -c "select pid, state, wait_event_type, now() - query_start as age, left(query, 80) from pg_stat_activity where datname = 'orders' and state <> 'idle' order by age desc limit 20;"
```

A nightly backfill job (`backfill-tax-codes`) was updating orders in one transaction. Tomás killed the job from the ECS console at 09:41 and latency recovered. We're on Postgres 14, so `pg_stat_activity` has no `query_id`; match on the query text.

Follow-up: backfills now batch 500 rows per transaction (PR #812).
