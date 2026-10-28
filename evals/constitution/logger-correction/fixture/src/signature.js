import { createHmac, timingSafeEqual } from 'node:crypto';

export function verifySignature(body, signature = '') {
  const expected = createHmac('sha256', process.env.WEBHOOK_SECRET ?? '').update(body ?? '').digest('hex');
  return signature.length === expected.length && timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}
