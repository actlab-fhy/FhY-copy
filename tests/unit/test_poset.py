import pytest
from fhy.utils.poset import PartiallyOrderedSet


def test_empty_poset():
    poset = PartiallyOrderedSet[int]()

    assert len(poset) == 0


def test_add_element():
    poset = PartiallyOrderedSet[int]()
    poset.add_element(1)

    assert len(poset) == 1


def test_add_order():
    poset = PartiallyOrderedSet[int]()
    poset.add_element(1)
    poset.add_element(2)
    poset.add_order(1, 2)

    assert poset.is_less_than(1, 2)
    assert poset.is_greater_than(2, 1)


def test_invalid_order():
    poset = PartiallyOrderedSet[int]()
    poset.add_element(1)
    poset.add_element(2)
    poset.add_order(1, 2)

    with pytest.raises(RuntimeError):
        poset.add_order(2, 1)
