import unittest

from app.clients.storage import StorageClient


class FakeTransport:
    def __init__(self, pages=None):
        self.pages = pages or {}
        self.deleted = []

    def get(self, path, params):
        return self.pages[params["cursor"]]

    def post(self, path, body):
        self.deleted.extend(body["keys"])


class StorageClientTest(unittest.TestCase):
    def test_lists_every_page(self):
        transport = FakeTransport(
            {None: {"items": ["a", "b"], "next_cursor": "c1"}, "c1": {"items": ["c"], "next_cursor": None}}
        )
        self.assertEqual(StorageClient(transport).list_objects("b"), ["a", "b", "c"])

    def test_deletes_in_batches(self):
        transport = FakeTransport()
        keys = [f"k{i}" for i in range(2500)]
        self.assertEqual(StorageClient(transport).delete_objects("b", keys), 2500)
        self.assertEqual(transport.deleted, keys)


if __name__ == "__main__":
    unittest.main()
