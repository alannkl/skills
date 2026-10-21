import unittest
from unittest import mock

from app import prices


class PriceTest(unittest.TestCase):
    def test_reads_from_service(self):
        with mock.patch.object(prices, "fetch_price", return_value=999):
            self.assertEqual(prices.price_cents("a"), 999)


if __name__ == "__main__":
    unittest.main()
