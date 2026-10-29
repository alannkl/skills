// Order total in cents: items plus shipping, free from 50.00.
export function orderTotal(cart) {
  const subtotal = cart.items.reduce((sum, item) => sum + item.priceCents * item.qty, 0);
  const shipping = subtotal >= 5000 ? 0 : 499;
  return subtotal + shipping;
}
