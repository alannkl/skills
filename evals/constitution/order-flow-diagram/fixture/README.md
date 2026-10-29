# shop-platform

Services for the web shop. Each folder under `services/` deploys on its own; they talk over HTTP or through the
event bus in `lib/bus.js` (RabbitMQ in production).

| Service | Owns |
| --- | --- |
| checkout | carts and placing orders |
| payments | charging cards |
| warehouse | stock, reservations and shipments |
| fulfillment | turning paid orders into shipments |
| notifications | customer emails |

Run one locally with `npm run dev -w services/<name>`.
