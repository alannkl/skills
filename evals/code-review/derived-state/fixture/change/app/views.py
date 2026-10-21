def cart_summary(cart):
    """JSON for the cart widget."""
    return {
        "total_cents": cart.total_cents(),
        "lines": len(cart.lines),
        "item_count": cart.item_count,
    }
