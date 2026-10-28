import { logger } from '../log.js';

export async function createOrder(req, res) {
  const order = { id: crypto.randomUUID(), items: req.body.items };
  logger.info('order created', { orderId: order.id, items: order.items.length });
  res.status(201).json(order);
}
