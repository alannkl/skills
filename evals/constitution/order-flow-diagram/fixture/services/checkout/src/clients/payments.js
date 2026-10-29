const BASE = process.env.PAYMENTS_URL;

export async function charge({ orderId, amountCents, paymentMethodId }) {
  const res = await fetch(`${BASE}/charges`, {
    method: "POST",
    headers: { "content-type": "application/json", "idempotency-key": orderId },
    body: JSON.stringify({ orderId, amountCents, paymentMethodId }),
  });
  if (res.status === 402) return { ok: false, reason: (await res.json()).reason };
  if (!res.ok) throw new Error(`payments ${res.status}`);
  return { ok: true, chargeId: (await res.json()).id };
}
