"""Retry helper shared by every outbound API client."""
import time

TRANSIENT_STATUSES = {429, 502, 503, 504}


def is_transient(exc):
    """Rate limiting, a gateway error, or a dropped or timed-out connection."""
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    return getattr(exc, "status", None) in TRANSIENT_STATUSES


def with_retry(fn, attempts=3, backoff=0.2, sleep=time.sleep):
    """Call fn, retrying transient failures with exponential backoff."""
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:
            if attempt == attempts - 1 or not is_transient(exc):
                raise
            sleep(backoff * 2**attempt)
