import { describe, expect, it } from "vitest";
import { createRefund } from "../src/services/refunds.js";

describe("createRefund", () => {
  it("refuses a second refund for the same order", async () => {
    expect(await createRefund({ order_id: "ord_1", amount_cents: 500 })).not.toBeNull();
    expect(await createRefund({ order_id: "ord_1", amount_cents: 500 })).toBeNull();
  });
});
