import unittest

from app.cart import Cart
from app.session import dump_cart, load_cart


class CartTest(unittest.TestCase):
    def test_total(self):
        cart = Cart()
        cart.add("a", 2, 500)
        cart.add("b", 1, 250)
        self.assertEqual(cart.total_cents(), 1250)

    def test_session_round_trip(self):
        cart = Cart()
        cart.add("a", 2, 500)
        self.assertEqual(load_cart(dump_cart(cart)), cart)

    def test_item_count_tracks_changes(self):
        cart = Cart()
        cart.add("a", 2, 500)
        cart.add("b", 1, 250)
        cart.set_quantity("a", 5)
        cart.remove("b")
        self.assertEqual(cart.item_count, 5)


if __name__ == "__main__":
    unittest.main()
