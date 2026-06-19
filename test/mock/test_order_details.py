"""Tests for get_order_details and get_orders_details."""

from click_and_drop_api.models.get_order_details_resource import GetOrderDetailsResource
from click_and_drop_api.simple.mock import MockClickAndDrop

from .helpers import make_order


def _create(api: MockClickAndDrop, *references: str) -> list[int]:
    response = api.create_orders([make_order(ref) for ref in references])
    return [o.order_identifier for o in response.created_orders]


# --- get_order_details ---


def test_get_order_details_by_id(api: MockClickAndDrop) -> None:
    (order_id,) = _create(api, "ref-det-1")
    details = api.get_order_details(order_id)
    assert details is not None
    assert isinstance(details, GetOrderDetailsResource)


def test_get_order_details_by_reference(api: MockClickAndDrop) -> None:
    _create(api, "ref-det-ref")
    details = api.get_order_details("ref-det-ref")
    assert details is not None
    assert details.order_reference == "ref-det-ref"


def test_get_order_details_not_found_returns_none(api: MockClickAndDrop) -> None:
    assert api.get_order_details(9999) is None
    assert api.get_order_details("nonexistent") is None


def test_get_order_details_has_correct_identifier(api: MockClickAndDrop) -> None:
    (order_id,) = _create(api, "ref-id-check")
    details = api.get_order_details(order_id)
    assert details.order_identifier == order_id


def test_get_order_details_initial_status_is_none(api: MockClickAndDrop) -> None:
    (order_id,) = _create(api, "ref-status-none")
    details = api.get_order_details(order_id)
    assert details.order_status is None


# --- get_orders_details ---


def test_get_orders_details_multiple(api: MockClickAndDrop) -> None:
    ids = _create(api, "d1", "d2", "d3")
    results = api.get_orders_details(ids)
    assert len(results) == 3


def test_get_orders_details_single_as_scalar(api: MockClickAndDrop) -> None:
    (order_id,) = _create(api, "ref-scalar")
    results = api.get_orders_details(order_id)
    assert len(results) == 1


# --- status reflected after update ---


def test_get_order_details_status_reflects_set_order_status(
    api: MockClickAndDrop,
) -> None:
    (order_id,) = _create(api, "ref-upd-status")
    api.set_order_status([order_id], "despatched")
    details = api.get_order_details(order_id)
    assert details.order_status == "despatched"


def test_get_order_details_status_reflects_update_orders(api: MockClickAndDrop) -> None:
    (order_id,) = _create(api, "ref-upd2")
    api.update_orders([order_id], status="new")
    details = api.get_order_details(order_id)
    assert details.order_status == "new"


def test_get_order_details_status_by_reference(api: MockClickAndDrop) -> None:
    _create(api, "ref-by-ref")
    api.set_order_status(["ref-by-ref"], "despatched")
    details = api.get_order_details("ref-by-ref")
    assert details.order_status == "despatched"


def test_get_orders_details_multiple_statuses(api: MockClickAndDrop) -> None:
    ids = _create(api, "ms1", "ms2")
    api.set_order_status([ids[0]], "despatched")
    api.set_order_status([ids[1]], "new")
    results = {d.order_identifier: d.order_status for d in api.get_orders_details(ids)}
    assert results[ids[0]] == "despatched"
    assert results[ids[1]] == "new"
