"""Feature flags, read from the flags service."""
import logging
import threading

log = logging.getLogger(__name__)


class FlagStore:
    def __init__(self, fetch, refresh_seconds=30):
        # fetch() returns {flag name: bool} from the flags service, or raises
        # after its 2 s timeout.
        self._fetch = fetch
        self._flags = fetch()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._refresh_loop, args=(refresh_seconds,), daemon=True
        )
        self._thread.start()

    def _refresh_loop(self, interval):
        while not self._stop.wait(interval):
            try:
                flags = self._fetch()
            except Exception:
                log.warning("flag refresh failed; keeping the last known flags", exc_info=True)
                continue
            with self._lock:
                self._flags = flags

    def enabled(self, name):
        with self._lock:
            return self._flags.get(name, False)

    def close(self):
        self._stop.set()
        self._thread.join()
