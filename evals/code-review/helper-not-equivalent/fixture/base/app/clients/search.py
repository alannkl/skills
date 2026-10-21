from app.retry import with_retry


class SearchClient:
    def __init__(self, transport):
        self.transport = transport

    def search(self, query, limit=20):
        return with_retry(lambda: self.transport.get("/search", {"q": query, "limit": limit}))
