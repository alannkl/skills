// Amounts are integer cents. See docs/refunds.md for the policy.

export function refundAmount(order, returnedSkus) {
  const returned = order.items.filter((item) => returnedSkus.includes(item.sku));
  const itemsTotal = returned.reduce((sum, item) => sum + item.price * item.quantity, 0);
  return itemsTotal + order.shipping;
}
