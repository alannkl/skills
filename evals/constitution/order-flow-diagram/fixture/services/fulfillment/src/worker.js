import { publish, subscribe } from "../../../lib/bus.js";

const WAREHOUSE = process.env.WAREHOUSE_URL;

async function post(path, body) {
  const res = await fetch(`${WAREHOUSE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`warehouse ${path} ${res.status}`);
  return res.json();
}

// A paid order becomes a reservation, then a shipment the warehouse picks and packs.
subscribe("order.paid", "fulfillment.order-paid", async ({ orderId, items }) => {
  const reservation = await post("/reservations", { orderId, items });
  const shipment = await post("/shipments", { orderId, reservationId: reservation.id });
  await publish("shipment.created", { orderId, shipmentId: shipment.id });
});
