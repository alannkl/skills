import { totalQuantity } from './totals.js';

export function packingSlip(invoice) {
  const rows = invoice.lines.map((line) => `${line.quantity} x ${line.sku}`);
  return [`Order ${invoice.id}`, ...rows, `Items: ${totalQuantity(invoice)}`].join('\n');
}
