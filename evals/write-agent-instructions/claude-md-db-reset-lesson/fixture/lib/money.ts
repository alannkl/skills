export function formatMoney(cents: number, currency = "USD"): string {
  // TODO: respect currency
  return "$" + (cents / 100).toFixed(2);
}
