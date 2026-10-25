# 2026-08-02 Duplicate orders for one checkout

Support ticket SUP-2291: a customer was charged once but got two order confirmation emails. No alert fired.

Looked up the customer's orders (customer `cus_Q81` from the ticket):

```
scripts/db-ro.sh -c "select id, status, total_cents, idempotency_key, created_at from orders where customer_id = 'cus_Q81' order by created_at desc limit 10;"
```

Two orders, `ord_60031` and `ord_60032`, 400 ms apart, same `idempotency_key`. Then the request logs for both:

```
aws logs start-query --log-group-name /ecs/orders-api \
  --start-time 1785657600 --end-time 1785661200 \
  --query-string 'fields @timestamp, requestId, orderId, msg | filter orderId in ["ord_60031","ord_60032"] | sort @timestamp asc'
```

Both requests passed the idempotency check before either committed: the unique index on `idempotency_key` was missing on the `orders` table after the July migration. `\d orders` on the replica confirmed it:

```
scripts/db-ro.sh -c "\d orders"
```

Fixed by restoring the unique index (migration `0047_orders_idempotency_unique`). Marco refunded the duplicate by hand in Stripe. Lesson: when duplicates show up, check constraints on the table before suspecting the client.
