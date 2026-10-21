"""Small caching helpers."""
import time


class TTLValue:
    """Hold one value, reloading it on access once it is older than ttl seconds."""

    def __init__(self, load, ttl, clock=time.monotonic):
        self._load = load
        self._ttl = ttl
        self._clock = clock
        self._value = None
        self._loaded_at = None

    def get(self):
        now = self._clock()
        if self._loaded_at is None or now - self._loaded_at >= self._ttl:
            self._value = self._load()
            self._loaded_at = now
        return self._value
