const express = require('express');
const orders = require('../repos/orders');

const router = express.Router();

router.get('/:id', async (req, res, next) => {
  try {
    const order = await orders.findOrder(req.params.id);
    if (!order) return res.status(404).json({ error: 'not found' });
    res.json(order);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
