import { subscribe } from "../../../lib/bus.js";
import { sendEmail } from "./email.js";

subscribe("order.paid", "notifications.order-paid", async ({ orderId, customerId }) => {
  await sendEmail(customerId, "order-confirmation", { orderId });
});

subscribe("shipment.created", "notifications.shipment-created", async ({ orderId, shipmentId }) => {
  await sendEmail(null, "shipping-update", { orderId, shipmentId });
});
