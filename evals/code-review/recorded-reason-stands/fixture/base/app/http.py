class HTTPError(Exception):
    """A non-2xx response from an upstream API."""

    def __init__(self, status, message=""):
        super().__init__(f"{status} {message}".strip())
        self.status = status
