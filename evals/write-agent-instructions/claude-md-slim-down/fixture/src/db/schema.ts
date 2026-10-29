export interface Invoice {
  id: string;
  customerId: string;
  amountCents: number;
  currency: string;
  issuedAt: string;
}
