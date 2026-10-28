export function orderTotal(order) {
  return order.items.reduce((sum, item) => sum + item.price * item.quantity, 0) + order.shipping;
}
