from decimal import Decimal

from apps.billing.models import Invoice
from apps.core.money import Money


def invoice_total(invoice: Invoice) -> Money:
    total = sum((li.unit_price * li.quantity for li in invoice.lineitems.all()), Decimal("0"))
    return Money(total, invoice.currency)
