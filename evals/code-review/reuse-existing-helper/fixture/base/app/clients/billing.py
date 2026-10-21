from app.pagination import iter_pages


class BillingClient:
    def __init__(self, transport):
        self.transport = transport

    def list_invoices(self, customer_id):
        def fetch(cursor, limit):
            return self.transport.get(
                f"/customers/{customer_id}/invoices", {"cursor": cursor, "limit": limit}
            )

        return list(iter_pages(fetch))
