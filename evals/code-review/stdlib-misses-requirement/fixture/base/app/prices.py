from app.pricing_service import fetch_price


def price_cents(sku):
    return fetch_price(sku)
