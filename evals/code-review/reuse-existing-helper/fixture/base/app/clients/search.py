from app.pagination import iter_pages


class SearchClient:
    def __init__(self, transport):
        self.transport = transport

    def all_results(self, query):
        def fetch(cursor, limit):
            return self.transport.get("/search", {"q": query, "cursor": cursor, "limit": limit})

        return list(iter_pages(fetch))
