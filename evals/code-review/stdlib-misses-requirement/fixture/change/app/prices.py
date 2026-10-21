from app.pricing_service import fetch_price
from app.ttl_lru import TTLLRUCache

_cache = TTLLRUCache(maxsize=10_000, ttl=600)


def price_cents(sku):
    return _cache.get(sku, fetch_price)
