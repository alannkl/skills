import { verifySignature } from '../signature.js';
import { markPaid, markFailed } from '../payments.js';

export async function paymentWebhook(req, res) {
  if (!verifySignature(req.rawBody, req.headers['x-signature'])) {
    console.log('webhook signature mismatch', req.headers['x-request-id']);
    return res.status(400).end();
  }
  const event = req.body;
  console.log('webhook received', event.type, event.id);
  switch (event.type) {
    case 'payment.succeeded':
      await markPaid(event.data.orderId);
      break;
    case 'payment.failed':
      await markFailed(event.data.orderId, event.data.reason);
      console.log('payment failed for order', event.data.orderId, event.data.reason);
      break;
    default:
      console.log('ignoring webhook type', event.type);
  }
  res.status(204).end();
}
