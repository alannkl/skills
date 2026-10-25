import pytest

from api.pagination import paginate


def test_first_page():
    p = paginate(list(range(45)), page=1, per_page=20)
    assert p.items == list(range(20))
    assert p.has_next


def test_last_page():
    p = paginate(list(range(45)), page=3, per_page=20)
    assert p.items == [40, 41, 42, 43, 44]
    assert not p.has_next


def test_page_zero_rejected():
    with pytest.raises(ValueError):
        paginate([1, 2, 3], page=0)
