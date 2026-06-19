"""Tests for MockClickAndDrop.delete_order / delete_orders."""

from click_and_drop_api.simple.mock import MockClickAndDrop

from .helpers import make_order


def test_delete_order_by_id(api: MockClickAndDrop):
    response = api.create_order(make_order())
    order_id = response.created_orders[0].order_identifier
    result = api.delete_order(order_id)
    assert len(result.deleted_orders) == 1
    assert len(result.errors) == 0
    assert api.get_order(order_id) is None


def test_delete_order_by_reference(api: MockClickAndDrop):
    api.create_order(make_order("del-ref"))
    result = api.delete_order("del-ref")
    assert len(result.deleted_orders) == 1
    assert api.get_order("del-ref") is None


def test_delete_order_not_found_returns_error(api: MockClickAndDrop):
    result = api.delete_order(9999)
    assert len(result.deleted_orders) == 0
    assert len(result.errors) == 1
    assert result.errors[0].code == "NOT_FOUND"


def test_delete_orders_batch(api: MockClickAndDrop):
    r = api.create_orders([make_order("d1"), make_order("d2")])
    ids = [o.order_identifier for o in r.created_orders]
    result = api.delete_orders(ids)
    assert len(result.deleted_orders) == 2
    assert len(result.errors) == 0


def test_delete_orders_partial_not_found(api: MockClickAndDrop):
    r = api.create_order(make_order())
    order_id = r.created_orders[0].order_identifier
    result = api.delete_orders([order_id, 9999])
    assert len(result.deleted_orders) == 1
    assert len(result.errors) == 1
