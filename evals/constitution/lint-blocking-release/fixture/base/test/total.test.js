import { test } from "node:test";
import assert from "node:assert/strict";
import { orderTotal } from "../src/checkout/total.js";

const cart = (...prices) => ({ items: prices.map((priceCents) => ({ priceCents, qty: 1 })) });

test("adds shipping under 50.00", () => {
  assert.equal(orderTotal(cart(1200, 800)), 2499);
});

test("ships free from 50.00", () => {
  assert.equal(orderTotal(cart(3000, 2500)), 5500);
});
