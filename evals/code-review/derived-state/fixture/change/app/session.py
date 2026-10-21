"""Serialize the cart to and from the session store."""
from dataclasses import asdict

from app.cart import Cart, Line


def dump_cart(cart):
    return {"lines": [asdict(line) for line in cart.lines], "item_count": cart.item_count}


def load_cart(data):
    return Cart(
        lines=[Line(**line) for line in data.get("lines", [])],
        item_count=data.get("item_count", 0),
    )
