from app.cache import TTLValue


class TaxTables:
    def __init__(self, fetch_tables):
        # fetch_tables() returns {region: rate} from the tax service.
        self._tables = TTLValue(fetch_tables, ttl=300)

    def rate(self, region):
        return self._tables.get()[region]
