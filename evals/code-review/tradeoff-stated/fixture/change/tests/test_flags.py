import unittest

from app.flags import FlagStore


class FlagStoreTest(unittest.TestCase):
    def test_unknown_flag_is_off(self):
        store = FlagStore(lambda: {"a": True})
        self.addCleanup(store.close)
        self.assertFalse(store.enabled("b"))

    def test_reads_flag(self):
        store = FlagStore(lambda: {"a": True})
        self.addCleanup(store.close)
        self.assertTrue(store.enabled("a"))

    def test_fetches_once_between_refreshes(self):
        calls = []

        def fetch():
            calls.append(1)
            return {"a": True}

        store = FlagStore(fetch, refresh_seconds=60)
        self.addCleanup(store.close)
        for _ in range(10):
            store.enabled("a")
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
