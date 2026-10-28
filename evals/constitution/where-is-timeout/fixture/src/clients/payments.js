import { config } from '../config.js';

// Payment calls must not be retried blindly, so this client does not use clients/http.js.
const TIMEOUT_MS = Number(process.env.PAYMENTS_TIMEOUT_MS ?? 8000);

export async function charge(customerId, amountCents, idempotencyKey) {
  const response = await fetch(`${config.payments.baseUrl}/charges`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'idempotency-key': idempotencyKey },
    body: JSON.stringify({ customer: customerId, amount: amountCents }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!response.ok) throw new Error(`charge failed: ${response.status}`);
  return response.json();
}
