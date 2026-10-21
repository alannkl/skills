import unittest

from app.clients.payments import PaymentsClient


class FakeTransport:
    def __init__(self, failures):
        self.failures = list(failures)
        self.calls = 0

    def post(self, path, body):
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return {"id": "ch_1", **body}


class PaymentsClientTest(unittest.TestCase):
    def test_retries_refused_connection(self):
        transport = FakeTransport([ConnectionRefusedError()])
        self.assertEqual(PaymentsClient(transport).charge("c1", 500)["id"], "ch_1")
        self.assertEqual(transport.calls, 2)

    def test_does_not_retry_timeout(self):
        transport = FakeTransport([TimeoutError()])
        with self.assertRaises(TimeoutError):
            PaymentsClient(transport).charge("c1", 500)
        self.assertEqual(transport.calls, 1)


if __name__ == "__main__":
    unittest.main()
