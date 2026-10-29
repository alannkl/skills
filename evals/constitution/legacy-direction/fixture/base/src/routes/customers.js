const express = require('express');
const db = require('../db');

const router = express.Router();

router.get('/:id', async (req, res, next) => {
  try {
    const rows = await db.query('SELECT id, name, email FROM customers WHERE id = $1', [req.params.id]);
    if (!rows.length) return res.status(404).json({ error: 'customer not found' });
    res.json(rows[0]);
  } catch (err) {
    next(err);
  }
});

router.get('/:id/orders', async (req, res, next) => {
  try {
    const rows = await db.query(
      'SELECT id, total_cents, status FROM orders WHERE customer_id = $1 ORDER BY created_at DESC',
      [req.params.id]);
    res.json(rows);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
