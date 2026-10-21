import time

from app.retry import is_transient


class RatesClient:
    def __init__(self, transport, sleep=time.sleep):
        self.transport = transport
        self.sleep = sleep

    def latest(self, base="USD"):
        # Not with_retry: it retries immediately with no delay, which hammers
        # the rates API during an outage. Back off between attempts instead.
        delay = 0.2
        for attempt in range(3):
            try:
                return self.transport.get("/rates/latest", {"base": base})
            except Exception as exc:
                if attempt == 2 or not is_transient(exc):
                    raise
            self.sleep(delay)
            delay *= 2
