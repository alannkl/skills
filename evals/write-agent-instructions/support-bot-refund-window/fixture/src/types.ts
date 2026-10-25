export type BillingInterval = "monthly" | "annual";

export interface Customer {
  id: string;
  firstName: string;
  plan: "classic" | "family" | "veggie";
  billingInterval: BillingInterval;
  createdAt: Date;
  lastChargeDate: string | null; // ISO date
}
