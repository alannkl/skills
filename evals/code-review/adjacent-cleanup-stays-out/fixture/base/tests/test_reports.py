import unittest

from app.reports import format_currency


class FormatCurrencyTest(unittest.TestCase):
    def test_whole_and_cents(self):
        self.assertEqual(format_currency(1505), "$15.05")


if __name__ == "__main__":
    unittest.main()
