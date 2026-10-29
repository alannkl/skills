export type Refund = { id: string; order_id: string; amount_cents: number; reason?: string };

const refunded = new Set<string>();

export async function createRefund(input: { order_id: string; amount_cents: number; reason?: string }): Promise<Refund | null> {
  if (refunded.has(input.order_id)) return null;
  refunded.add(input.order_id);
  return { id: `re_${Date.now()}`, ...input };
}
