// Read-through cache for product prices, so the product page stops hitting Postgres on every view.
const TTL_MS = 10 * 60 * 1000;
const entries = new Map();

async function cached(key, load) {
  const hit = entries.get(key);
  if (hit && hit.expires > Date.now()) return hit.value;
  const value = await load();
  entries.set(key, { value, expires: Date.now() + TTL_MS });
  return value;
}

function clear() {
  entries.clear();
}

module.exports = { cached, clear, TTL_MS };
