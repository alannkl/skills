import unittest

from app.flags import FlagStore


class FlagStoreTest(unittest.TestCase):
    def test_unknown_flag_is_off(self):
        self.assertFalse(FlagStore(lambda: {"a": True}).enabled("b"))

    def test_reads_flag(self):
        self.assertTrue(FlagStore(lambda: {"a": True}).enabled("a"))


if __name__ == "__main__":
    unittest.main()
