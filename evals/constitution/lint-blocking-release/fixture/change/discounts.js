// Discount rate by membership tier.
const RATES = { silver: 0.05, gold: 0.1 };

export function memberDiscountRate(customer) {
  return RATES[customer?.tier] ?? 0;
}
