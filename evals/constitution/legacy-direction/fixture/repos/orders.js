const db = require('../db');

// SQL for orders lives here; routes call these functions instead of querying directly.
async function findOrder(id) {
  const rows = await db.query('SELECT id, customer_id, total_cents, status FROM orders WHERE id = $1', [id]);
  return rows[0] || null;
}

module.exports = { findOrder };
