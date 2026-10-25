import { describe, expect, it } from "vitest";
import { buildSystemPrompt } from "./prompt";

const customer = {
  id: "c_1",
  firstName: "Ana",
  plan: "family" as const,
  billingInterval: "monthly" as const,
  createdAt: new Date("2025-02-01"),
  lastChargeDate: "2026-10-01",
};

describe("buildSystemPrompt", () => {
  it("includes customer context", () => {
    const p = buildSystemPrompt(customer, []);
    expect(p).toContain("Name: Ana");
    expect(p).toContain("family (monthly)");
  });

  it("numbers kb snippets", () => {
    const p = buildSystemPrompt(customer, ["a", "b"]);
    expect(p).toContain("[2] b");
  });
});
