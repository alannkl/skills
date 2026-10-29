export async function handleStripeEvent(signature: string | string[] | undefined, body: unknown): Promise<void> {
  if (typeof signature !== "string") throw new Error("missing stripe-signature header");
  const event = body as { type?: string };
  if (event.type === "charge.refunded") {
    // Refund bookkeeping happens in the refunds service; nothing to do here yet.
  }
}
