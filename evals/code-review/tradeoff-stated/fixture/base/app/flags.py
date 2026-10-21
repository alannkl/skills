"""Feature flags, read from the flags service."""


class FlagStore:
    def __init__(self, fetch):
        # fetch() returns {flag name: bool} from the flags service, or raises
        # after its 2 s timeout.
        self._fetch = fetch

    def enabled(self, name):
        return self._fetch().get(name, False)
