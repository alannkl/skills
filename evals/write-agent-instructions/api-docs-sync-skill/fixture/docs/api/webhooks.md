# Webhooks

### POST /webhooks/stripe

Point your Stripe account's webhook at this endpoint so paid and refunded charges update the matching orders.

| Header | Required | Description |
| --- | --- | --- |
| `Stripe-Signature` | yes | Set by Stripe. Events with a missing or invalid signature are rejected. |

Returns `204` once the event is accepted.

In the Stripe dashboard, add `https://api.shopfront.dev/webhooks/stripe` as an endpoint and select `charge.succeeded` and `charge.refunded`.
