import { test } from 'node:test';
import assert from 'node:assert/strict';
import { refundAmount } from '../src/refunds.js';

const order = {
  shipping: 599,
  items: [
    { sku: 'A', price: 1000, quantity: 2 },
    { sku: 'B', price: 2500, quantity: 1 },
  ],
};

test('full return refunds items and shipping', () => {
  assert.equal(refundAmount(order, ['A', 'B']), 5099);
});

test('partial return refunds only the returned items', () => {
  assert.equal(refundAmount(order, ['B']), 2500);
});

test('returning nothing refunds nothing', () => {
  assert.equal(refundAmount(order, []), 0);
});
