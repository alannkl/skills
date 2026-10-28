// All amounts are integer cents.

export function lineSubtotal(line) {
  return line.unitPrice * line.quantity;
}

export function applyDiscount(subtotal, discount) {
  if (discount.type === 'percent') {
    return Math.round(subtotal * discount.value);
  }
  return Math.min(discount.value, subtotal);
}

export function invoiceTotal(invoice) {
  const subtotal = invoice.lines.reduce((sum, line) => sum + lineSubtotal(line), 0);
  const discount = invoice.discount ? applyDiscount(subtotal, invoice.discount) : 0;
  return subtotal - discount;
}

export function totalQuantity(invoice) {
  return invoice.lines.length;
}
