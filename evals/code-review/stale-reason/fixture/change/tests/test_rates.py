import unittest

from app.clients.rates import RatesClient
from app.http import HTTPError


class FakeTransport:
    def __init__(self, failures):
        self.failures = list(failures)

    def get(self, path, params):
        if self.failures:
            raise self.failures.pop(0)
        return {"base": params["base"], "EUR": 0.92}


class RatesClientTest(unittest.TestCase):
    def test_backs_off_between_retries(self):
        sleeps = []
        client = RatesClient(FakeTransport([HTTPError(503), HTTPError(503)]), sleep=sleeps.append)
        self.assertEqual(client.latest()["EUR"], 0.92)
        self.assertEqual(sleeps, [0.2, 0.4])


if __name__ == "__main__":
    unittest.main()
