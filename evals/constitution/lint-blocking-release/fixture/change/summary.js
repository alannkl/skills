import { orderTotal } from "./total.js";

// What the checkout page shows before the customer pays.
export function checkoutSummary(cart, customer) {
  return { items: cart.items.length, totalCents: orderTotal(cart, customer) };
}
