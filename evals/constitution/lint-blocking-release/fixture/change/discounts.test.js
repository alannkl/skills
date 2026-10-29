import { test } from "node:test";
import assert from "node:assert/strict";
import { memberDiscountRate } from "../src/checkout/discounts.js";

test("gold members get 10%", () => {
  assert.equal(memberDiscountRate({ tier: "gold" }), 0.1);
});

test("guests get nothing", () => {
  assert.equal(memberDiscountRate(undefined), 0);
});
