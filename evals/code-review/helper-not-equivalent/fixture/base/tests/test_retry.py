import unittest

from app.http import HTTPError
from app.retry import with_retry


class WithRetryTest(unittest.TestCase):
    def test_retries_transient_then_succeeds(self):
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise HTTPError(503)
            return "ok"

        self.assertEqual(with_retry(flaky, sleep=lambda s: None), "ok")
        self.assertEqual(len(calls), 3)

    def test_does_not_retry_client_errors(self):
        calls = []

        def bad():
            calls.append(1)
            raise HTTPError(400)

        with self.assertRaises(HTTPError):
            with_retry(bad, sleep=lambda s: None)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
