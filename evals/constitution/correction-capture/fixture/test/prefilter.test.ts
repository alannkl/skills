import { test } from "node:test";
import assert from "node:assert/strict";
import { isObviousCorrection } from "../src/prefilter.js";

test("catches an obvious correction", () => {
  assert.equal(isObviousCorrection("No, that's wrong, use the staging db"), true);
});

test("leaves a normal request alone", () => {
  assert.equal(isObviousCorrection("can you add a retry here"), false);
});
