"""The one place billing code talks to Stripe."""

from decimal import Decimal

import stripe


def charge(customer_id: str, amount: Decimal, currency: str = "usd") -> stripe.PaymentIntent:
    cents = int((amount * 100).to_integral_value())
    return stripe.PaymentIntent.create(customer=customer_id, amount=cents, currency=currency, confirm=True)
