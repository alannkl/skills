import { publish } from "../../../lib/bus.js";
import { stockLevels } from "./clients/warehouse.js";
import { charge } from "./clients/payments.js";
import { orders } from "./db.js";

export async function placeOrder(cart, paymentMethodId) {
  const stock = await stockLevels(cart.items.map((i) => i.sku));
  const short = cart.items.filter((i) => (stock[i.sku] ?? 0) < i.qty);
  if (short.length) return { status: "out_of_stock", skus: short.map((i) => i.sku) };

  const order = await orders.create({ customerId: cart.customerId, items: cart.items, status: "pending" });
  const payment = await charge({ orderId: order.id, amountCents: cart.totalCents, paymentMethodId });
  if (!payment.ok) {
    await orders.update(order.id, { status: "payment_failed" });
    return { status: "payment_failed", reason: payment.reason };
  }

  await orders.update(order.id, { status: "paid", chargeId: payment.chargeId });
  await publish("order.paid", { orderId: order.id, customerId: cart.customerId, items: cart.items });
  return { status: "paid", orderId: order.id };
}
