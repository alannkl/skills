"""Cursor pagination shared by the API clients."""


def iter_pages(fetch_page, page_size=100):
    """Yield every item from a cursor-paginated endpoint.

    fetch_page(cursor, limit) returns {"items": [...], "next_cursor": str | None}.
    """
    cursor = None
    while True:
        page = fetch_page(cursor, page_size)
        yield from page["items"]
        cursor = page.get("next_cursor")
        if not cursor:
            return
