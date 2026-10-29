const db = require('../db');

// SQL for users lives here; routes call these functions instead of querying directly.
async function findUser(id) {
  const rows = await db.query('SELECT id, email, created_at FROM users WHERE id = $1', [id]);
  return rows[0] || null;
}

module.exports = { findUser };
