import { test } from 'node:test';
import assert from 'node:assert/strict';
import { orderTotal } from '../src/orders.js';

test('order total includes shipping', () => {
  const order = { shipping: 599, items: [{ sku: 'A', price: 1000, quantity: 2 }] };
  assert.equal(orderTotal(order), 2599);
});
