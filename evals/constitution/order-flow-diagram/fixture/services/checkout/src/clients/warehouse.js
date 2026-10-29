const BASE = process.env.WAREHOUSE_URL;

// Units available per SKU, for the cart page and the check before an order is placed.
export async function stockLevels(skus) {
  const res = await fetch(`${BASE}/stock?skus=${skus.join(",")}`);
  if (!res.ok) throw new Error(`warehouse stock ${res.status}`);
  return res.json();
}
