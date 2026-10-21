import unittest

from app.pagination import iter_pages


class IterPagesTest(unittest.TestCase):
    def test_follows_cursor_until_exhausted(self):
        pages = {None: {"items": [1, 2], "next_cursor": "a"}, "a": {"items": [3], "next_cursor": None}}
        self.assertEqual(list(iter_pages(lambda cursor, limit: pages[cursor])), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
