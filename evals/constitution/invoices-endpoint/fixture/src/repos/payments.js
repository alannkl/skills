import { pool } from '../db/raw.js';

const toPayment = (row) => ({
  id: row.id,
  invoiceId: row.invoice_id,
  amountCents: row.amount_cents,
  paidAt: row.paid_at,
});

export async function listByInvoice(invoiceId) {
  const { rows } = await pool.query(
    'SELECT id, invoice_id, amount_cents, paid_at FROM payments WHERE invoice_id = $1 ORDER BY paid_at',
    [invoiceId],
  );
  return rows.map(toPayment);
}
