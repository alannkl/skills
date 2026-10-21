class PaymentsClient:
    def __init__(self, transport):
        self.transport = transport

    def charge(self, customer_id, amount_cents):
        # Not with_retry: it also retries timeouts and 5xx responses, which can
        # arrive after the processor has already charged the card, and the
        # payments API has no idempotency keys. Retry only a refused
        # connection, when nothing was sent.
        for attempt in range(2):
            try:
                return self.transport.post(
                    "/charges", {"customer": customer_id, "amount": amount_cents}
                )
            except ConnectionRefusedError:
                if attempt == 1:
                    raise
