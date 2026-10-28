import { logger } from './log.js';

const status = new Map();

export async function markPaid(orderId) {
  status.set(orderId, 'paid');
  logger.info('order paid', { orderId });
}

export async function markFailed(orderId, reason) {
  status.set(orderId, 'failed');
  logger.warn('order payment failed', { orderId, reason });
}
