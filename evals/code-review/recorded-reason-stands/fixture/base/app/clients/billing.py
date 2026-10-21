from app.retry import with_retry


class BillingClient:
    def __init__(self, transport):
        self.transport = transport

    def get_invoice(self, invoice_id):
        return with_retry(lambda: self.transport.get(f"/invoices/{invoice_id}"))
