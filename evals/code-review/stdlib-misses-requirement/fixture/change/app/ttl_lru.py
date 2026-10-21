"""LRU cache whose entries also expire after a fixed age."""
import time
from collections import OrderedDict


class TTLLRUCache:
    def __init__(self, maxsize, ttl, clock=time.monotonic):
        self._maxsize = maxsize
        self._ttl = ttl
        self._clock = clock
        self._entries = OrderedDict()  # key -> (stored_at, value)

    def get(self, key, load):
        now = self._clock()
        entry = self._entries.get(key)
        if entry is not None and now - entry[0] < self._ttl:
            self._entries.move_to_end(key)
            return entry[1]
        value = load(key)
        self._entries[key] = (now, value)
        self._entries.move_to_end(key)
        if len(self._entries) > self._maxsize:
            self._entries.popitem(last=False)
        return value
