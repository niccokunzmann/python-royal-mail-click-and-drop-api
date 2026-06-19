"""Tests for MockClickAndDrop.get_order / get_orders."""

from click_and_drop_api.simple.mock import MockClickAndDrop

from .helpers import make_order


def test_get_order_by_id(api: MockClickAndDrop):
    response = api.create_order(make_order("ref-x"))
    order_id = response.created_orders[0].order_identifier
    order = api.get_order(order_id)
    assert order is not None
    assert order.order_reference == "ref-x"


def test_get_order_by_reference(api: MockClickAndDrop):
    api.create_order(make_order("ref-y"))
    order = api.get_order("ref-y")
    assert order is not None
    assert order.order_reference == "ref-y"


def test_get_order_not_found_returns_none(api: MockClickAndDrop):
    assert api.get_order(9999) is None
    assert api.get_order("nonexistent") is None


def test_get_orders_multiple(api: MockClickAndDrop):
    r = api.create_orders([make_order("r1"), make_order("r2")])
    ids = [o.order_identifier for o in r.created_orders]
    orders = api.get_orders(ids)
    assert len(orders) == 2


def test_get_orders_mixed_id_and_ref(api: MockClickAndDrop):
    r = api.create_orders([make_order("alpha"), make_order("beta")])
    id1 = r.created_orders[0].order_identifier
    orders = api.get_orders([id1, "beta"])
    assert len(orders) == 2
