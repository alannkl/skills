export type Order = { id: string; status: "pending" | "paid" | "shipped"; total_cents: number };

const orders: Order[] = [];

export async function listOrders(query: { status?: Order["status"]; limit?: number }): Promise<Order[]> {
  const matching = query.status ? orders.filter((o) => o.status === query.status) : orders;
  return matching.slice(0, query.limit ?? 20);
}

export async function getOrder(id: string): Promise<Order | undefined> {
  return orders.find((o) => o.id === id);
}
