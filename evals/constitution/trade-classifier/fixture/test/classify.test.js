import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { classify } from '../src/classify.js';

const load = (name) => JSON.parse(readFileSync(new URL(`../fixtures/${name}`, import.meta.url)));

test('uniswap ETH buy', () => {
  const tx = load('trades/uni-buy-pepe-eth.json');
  assert.deepEqual(classify(tx), tx.expected);
});

test('1inch USDC sell', () => {
  const tx = load('trades/oneinch-sell-mog-usdc.json');
  assert.deepEqual(classify(tx), tx.expected);
});
