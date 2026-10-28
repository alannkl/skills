import { test } from 'node:test';
import assert from 'node:assert/strict';
import { invoiceTotal, lineSubtotal } from '../src/totals.js';
import { CODES } from '../src/codes.js';

const lines = [
  { sku: 'MUG', unitPrice: 1200, quantity: 2 },
  { sku: 'TEE', unitPrice: 2500, quantity: 1 },
];

test('line subtotal multiplies price by quantity', () => {
  assert.equal(lineSubtotal(lines[0]), 2400);
});

test('invoice total without a discount', () => {
  assert.equal(invoiceTotal({ lines }), 4900);
});

test('fixed discount comes off the subtotal', () => {
  assert.equal(invoiceTotal({ lines, discount: CODES.FLAT500 }), 4400);
});
