const express = require('express');
const db = require('../db');

const router = express.Router();

router.get('/:id', async (req, res, next) => {
  try {
    const rows = await db.query('SELECT * FROM carts WHERE id = $1', [req.params.id]);
    if (!rows.length) return res.status(404).json({ error: 'not found' });
    res.json(rows[0]);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
