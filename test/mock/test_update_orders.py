"""Tests for update_orders and set_order_* methods."""

from datetime import datetime, timezone

from click_and_drop_api.simple.mock import MockClickAndDrop

from .helpers import make_order


def _create_orders(api: MockClickAndDrop, *references: str) -> list[int]:
    """Helper: create orders and return their integer identifiers."""
    response = api.create_orders([make_order(ref) for ref in references])
    return [o.order_identifier for o in response.created_orders]


# --- update_orders ---


def test_update_orders_by_id_returns_updated(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-upd-1")
    response = api.update_orders([order_id], status="despatched")
    assert len(response.updated_orders) == 1
    assert len(response.errors) == 0


def test_update_orders_by_reference(api: MockClickAndDrop):
    _create_orders(api, "ref-upd-ref")
    response = api.update_orders(["ref-upd-ref"], status="despatched")
    assert len(response.updated_orders) == 1


def test_update_orders_multiple(api: MockClickAndDrop):
    ids = _create_orders(api, "ref-m1", "ref-m2", "ref-m3")
    response = api.update_orders(ids, status="new")
    assert len(response.updated_orders) == 3
    assert len(response.errors) == 0


def test_update_orders_all_fields(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-all-fields")
    despatch = datetime(2026, 4, 5, tzinfo=timezone.utc)
    response = api.update_orders(
        [order_id],
        status="despatched",
        tracking_number="TRK123",
        despatch_date=despatch,
        shipping_carrier="DHL",
        shipping_service="express",
    )
    assert len(response.updated_orders) == 1


def test_update_orders_no_kwargs(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-no-kwargs")
    response = api.update_orders([order_id])
    assert len(response.updated_orders) == 1


def test_update_orders_empty_list(api: MockClickAndDrop):
    response = api.update_orders([])
    assert response.updated_orders == []
    assert response.errors == []


# --- set_order_status ---


def test_set_order_status_by_id(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-status-1")
    response = api.set_order_status([order_id], "despatched")
    assert len(response.updated_orders) == 1
    assert response.updated_orders[0].order_identifier == order_id


def test_set_order_status_by_reference(api: MockClickAndDrop):
    _create_orders(api, "ref-status-ref")
    response = api.set_order_status(["ref-status-ref"], "new")
    assert len(response.updated_orders) == 1
    assert response.updated_orders[0].order_reference == "ref-status-ref"


def test_set_order_status_multiple(api: MockClickAndDrop):
    ids = _create_orders(api, "s1", "s2")
    response = api.set_order_status(ids, "despatched")
    assert len(response.updated_orders) == 2


def test_set_order_status_valid_values(api: MockClickAndDrop):
    for status in ("new", "despatched", "despatchedByOtherCourier"):
        (order_id,) = _create_orders(api, f"ref-{status}")
        response = api.set_order_status([order_id], status)
        assert len(response.updated_orders) == 1


# --- set_order_tracking_number ---


def test_set_order_tracking_number_by_id(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-track-1")
    response = api.set_order_tracking_number([order_id], "TRK999")
    assert len(response.updated_orders) == 1
    assert response.updated_orders[0].order_identifier == order_id


def test_set_order_tracking_number_multiple(api: MockClickAndDrop):
    ids = _create_orders(api, "trk1", "trk2")
    response = api.set_order_tracking_number(ids, "TRKBATCH")
    assert len(response.updated_orders) == 2


# --- set_order_despatch_date ---


def test_set_order_despatch_date_by_id(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-desp-1")
    despatch = datetime(2026, 4, 10, tzinfo=timezone.utc)
    response = api.set_order_despatch_date([order_id], despatch)
    assert len(response.updated_orders) == 1


def test_set_order_despatch_date_multiple(api: MockClickAndDrop):
    ids = _create_orders(api, "desp1", "desp2")
    despatch = datetime(2026, 4, 10, tzinfo=timezone.utc)
    response = api.set_order_despatch_date(ids, despatch)
    assert len(response.updated_orders) == 2


# --- set_order_shipping_carrier ---


def test_set_order_shipping_carrier_by_id(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-carrier-1")
    response = api.set_order_shipping_carrier([order_id], "DHL")
    assert len(response.updated_orders) == 1


def test_set_order_shipping_carrier_multiple(api: MockClickAndDrop):
    ids = _create_orders(api, "car1", "car2")
    response = api.set_order_shipping_carrier(ids, "UPS")
    assert len(response.updated_orders) == 2


# --- set_order_shipping_service ---


def test_set_order_shipping_service_by_id(api: MockClickAndDrop):
    (order_id,) = _create_orders(api, "ref-svc-1")
    response = api.set_order_shipping_service([order_id], "express")
    assert len(response.updated_orders) == 1


def test_set_order_shipping_service_multiple(api: MockClickAndDrop):
    ids = _create_orders(api, "svc1", "svc2")
    response = api.set_order_shipping_service(ids, "standard")
    assert len(response.updated_orders) == 2


# --- batching (max_order_count boundary) ---


def test_update_orders_batches_correctly():
    api = MockClickAndDrop()
    api.max_order_count = 2
    ids = _create_orders(api, "b1", "b2", "b3")
    response = api.update_orders(ids, status="despatched")
    assert len(response.updated_orders) == 3


def test_set_order_status_batches_correctly():
    api = MockClickAndDrop()
    api.max_order_count = 2
    ids = _create_orders(api, "bs1", "bs2", "bs3")
    response = api.set_order_status(ids, "new")
    assert len(response.updated_orders) == 3
