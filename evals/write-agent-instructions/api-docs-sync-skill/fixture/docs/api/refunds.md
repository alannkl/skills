# Refunds

### POST /refunds

Refunds all or part of an order.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `order_id` | string | yes | The order to refund. |
| `amount_cents` | integer | yes | Amount to refund, in cents. `1250` refunds 12.50. |
| `reason` | string | no | Shown to the customer on the refund receipt. |

Returns `201` with the refund, or `409` when the order is already refunded.

```bash
curl -X POST https://api.shopfront.dev/refunds -H "Authorization: Bearer $SHOPFRONT_TOKEN" \
  -H "Content-Type: application/json" -d '{"order_id": "ord_8Kd2", "amount_cents": 1250, "reason": "Damaged in transit"}'
```
