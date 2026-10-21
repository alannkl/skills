import unittest

from app.clients.profiles import ProfileClient
from app.http import HTTPError


class FakeTransport:
    def __init__(self, conflicts):
        self.conflicts = conflicts
        self.puts = []

    def get(self, path):
        return {"etag": f"v{len(self.puts)}", "body": {"display_name": "old", "bio": "hi"}}

    def put(self, path, body, headers):
        self.puts.append(headers["If-Match"])
        if self.conflicts:
            self.conflicts -= 1
            raise HTTPError(412)
        return body


class ProfileClientTest(unittest.TestCase):
    def test_rereads_after_conflict(self):
        transport = FakeTransport(conflicts=1)
        body = ProfileClient(transport).update_display_name("u1", "New")
        self.assertEqual(body, {"display_name": "New", "bio": "hi"})
        self.assertEqual(transport.puts, ["v0", "v1"])

    def test_gives_up_after_three_conflicts(self):
        with self.assertRaises(HTTPError):
            ProfileClient(FakeTransport(conflicts=3)).update_display_name("u1", "New")


if __name__ == "__main__":
    unittest.main()
