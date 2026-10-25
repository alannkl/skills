from celery import shared_task

from apps.billing.models import Invoice
from apps.billing.emails import send_invoice_email


@shared_task(bind=True, max_retries=3)
def send_invoice(self, invoice_id: int) -> None:
    invoice = Invoice.objects.get(pk=invoice_id)
    send_invoice_email(invoice)
    invoice.sent = True
    invoice.save(update_fields=["sent"])
