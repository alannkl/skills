# 2026-09-19 Payment failure alert, false alarm

`#orders-alerts`: "payment_failed rate > 5% (15 min)". On call: Priya.

Counted failures by reason in the last hour:

```
aws logs start-query --log-group-name /ecs/orders-api \
  --start-time $(date -d '-1 hour' +%s) --end-time $(date +%s) \
  --query-string 'filter msg = "payment_failed" | stats count(*) by reason | sort count(*) desc'
```

92% were `card_declined` from a single merchant test account running a load test against production (`acct_test_77`). No code or provider problem. Cross-checked in the DB that real customer payments were normal:

```
scripts/db-ro.sh -c "select status, count(*) from payments where created_at > now() - interval '1 hour' group by status;"
```

Closed as not an incident; asked the merchant team to use staging. We considered restarting the service (`aws ecs update-service --cluster prod --service orders-api --force-new-deployment`) before finding the cause; don't restart without the on-call lead agreeing, it drops in-flight webhooks.
