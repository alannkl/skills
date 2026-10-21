import unittest

from app.ttl_lru import TTLLRUCache


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class TTLLRUCacheTest(unittest.TestCase):
    def test_reloads_after_ttl(self):
        clock, loads = Clock(), []

        def load(key):
            loads.append(key)
            return len(loads)

        cache = TTLLRUCache(maxsize=10, ttl=600, clock=clock)
        self.assertEqual(cache.get("a", load), 1)
        clock.now = 599
        self.assertEqual(cache.get("a", load), 1)
        clock.now = 600
        self.assertEqual(cache.get("a", load), 2)

    def test_evicts_least_recently_used(self):
        cache = TTLLRUCache(maxsize=2, ttl=600, clock=Clock())
        cache.get("a", str.upper)
        cache.get("b", str.upper)
        cache.get("a", str.upper)
        cache.get("c", str.upper)
        reloaded = []

        def load(key):
            reloaded.append(key)
            return key

        cache.get("b", load)
        self.assertEqual(reloaded, ["b"])


if __name__ == "__main__":
    unittest.main()
