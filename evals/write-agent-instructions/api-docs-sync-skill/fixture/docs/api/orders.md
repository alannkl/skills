# Orders

### GET /orders

Lists your orders, newest first.

| Parameter | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `status` | query | string | no | One of `pending`, `paid`, `shipped`. |
| `limit` | query | integer | no | Orders per page, at most 100. |

Returns `200` with an array of orders.

```bash
curl "https://api.shopfront.dev/orders?status=paid&limit=20" -H "Authorization: Bearer $SHOPFRONT_TOKEN"
```

### GET /orders/{id}

Gets one order.

| Parameter | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | string | yes | The order ID, such as `ord_8Kd2`. |

Returns `200` with the order, or `404` when no order has this ID.

```bash
curl https://api.shopfront.dev/orders/ord_8Kd2 -H "Authorization: Bearer $SHOPFRONT_TOKEN"
```
