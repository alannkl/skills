import unittest

from app.reports import format_currency


class FormatCurrencyTest(unittest.TestCase):
    def test_whole_and_cents(self):
        self.assertEqual(format_currency(1505), "$15.05")

    def test_negative(self):
        self.assertEqual(format_currency(-150), "-$1.50")

    def test_negative_under_one_dollar(self):
        self.assertEqual(format_currency(-5), "-$0.05")


if __name__ == "__main__":
    unittest.main()
