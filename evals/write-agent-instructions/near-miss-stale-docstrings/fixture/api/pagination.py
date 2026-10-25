"""Offset pagination helpers for list endpoints.

Pages are 0-indexed: the first page is page 0.
"""

from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

T = TypeVar("T")

MAX_PER_PAGE = 100


@dataclass
class Page(Generic[T]):
    items: Sequence[T]
    page: int
    per_page: int
    total: int

    @property
    def has_next(self) -> bool:
        # page is 0-based, so the last page is total // per_page
        return self.page * self.per_page < self.total


def paginate(items: Sequence[T], page: int = 1, per_page: int = 20) -> Page[T]:
    """Return one page of ``items``.

    Args:
        items: The full, already-sorted sequence.
        page: Zero-based page number. Page 0 is the first page.
        per_page: Items per page, capped at MAX_PER_PAGE.

    Raises:
        ValueError: if ``page`` is negative.
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    per_page = min(per_page, MAX_PER_PAGE)
    # skip the first page * per_page items
    start = (page - 1) * per_page
    return Page(items[start : start + per_page], page, per_page, len(items))
