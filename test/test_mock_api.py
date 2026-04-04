"""Tests for MockClickAndDrop."""

from datetime import datetime, timezone

import pytest

from click_and_drop_api.models.order_field_response import OrderFieldResponse
from click_and_drop_api.simple.shipping_test_result import ShippingTestResult
from click_and_drop_api.simple.mock import MockClickAndDrop
from click_and_drop_api.simple.types import (
    Address,
    CreateOrder,
    RecipientDetails,
)


@pytest.fixture(params=[1, 100])
def api(request):
    api = MockClickAndDrop()
    api.max_order_count = request.param
    return api


def _make_order(reference: str = "test-ref-001") -> CreateOrder:
    return CreateOrder(
        order_reference=reference,
        order_date=datetime.now(timezone.utc),
        subtotal=10.00,
        shipping_cost_charged=0.00,
        total=10.00,
        currency_code="GBP",
        recipient=RecipientDetails(
            address=Address(
                full_name="Test User",
                address_line1="1 Test Street",
                city="London",
                postcode="SW1A 1AA",
                country_code="GB",
            )
        ),
    )


# --- Constructor ---


def test_default_key(api):
    assert api.key == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def test_custom_key():
    key = "11111111-2222-3333-4444-555555555555"
    api = MockClickAndDrop(key=key)
    assert api.key == key


def test_invalid_key_type():
    with pytest.raises(TypeError):
        MockClickAndDrop(key=12345)


def test_invalid_key_too_short():
    with pytest.raises(ValueError):
        MockClickAndDrop(key="short")


def test_invalid_key_whitespace():
    with pytest.raises(ValueError):
        MockClickAndDrop(key="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeee ee")


# --- get_version ---


def test_get_version_returns_mock_release(api):
    version = api.get_version()
    assert version.release == "1.0.0-mock"
    assert version.commit == "mock"
    assert version.build == "mock"
    assert isinstance(version.release_date, datetime)


# --- create_order / create_orders ---


def test_create_order_single(api):
    response = api.create_order(_make_order())
    assert response.success_count == 1
    assert response.errors_count == 0
    assert len(response.created_orders) == 1
    assert len(response.failed_orders) == 0


def test_create_orders_batch(api):
    response = api.create_orders([_make_order("ref-a"), _make_order("ref-b")])
    assert response.success_count == 2
    assert len(response.created_orders) == 2


def test_created_order_has_correct_reference(api):
    response = api.create_order(_make_order("my-ref"))
    assert response.created_orders[0].order_reference == "my-ref"


def test_created_order_has_integer_identifier(api):
    response = api.create_order(_make_order())
    assert isinstance(response.created_orders[0].order_identifier, int)


def test_order_identifiers_increment(api):
    r1 = api.create_order(_make_order("ref-1"))
    r2 = api.create_order(_make_order("ref-2"))
    id1 = r1.created_orders[0].order_identifier
    id2 = r2.created_orders[0].order_identifier
    assert id2 == id1 + 1


# --- get_order / get_orders ---


def test_get_order_by_id(api):
    response = api.create_order(_make_order("ref-x"))
    order_id = response.created_orders[0].order_identifier
    order = api.get_order(order_id)
    assert order is not None
    assert order.order_reference == "ref-x"


def test_get_order_by_reference(api):
    api.create_order(_make_order("ref-y"))
    order = api.get_order("ref-y")
    assert order is not None
    assert order.order_reference == "ref-y"


def test_get_order_not_found_returns_none(api):
    assert api.get_order(9999) is None
    assert api.get_order("nonexistent") is None


def test_get_orders_multiple(api):
    r = api.create_orders([_make_order("r1"), _make_order("r2")])
    ids = [o.order_identifier for o in r.created_orders]
    orders = api.get_orders(ids)
    assert len(orders) == 2


def test_get_orders_mixed_id_and_ref(api):
    r = api.create_orders([_make_order("alpha"), _make_order("beta")])
    id1 = r.created_orders[0].order_identifier
    orders = api.get_orders([id1, "beta"])
    assert len(orders) == 2


# --- delete_order / delete_orders ---


def test_delete_order_by_id(api):
    response = api.create_order(_make_order())
    order_id = response.created_orders[0].order_identifier
    result = api.delete_order(order_id)
    assert len(result.deleted_orders) == 1
    assert len(result.errors) == 0
    assert api.get_order(order_id) is None


def test_delete_order_by_reference(api):
    api.create_order(_make_order("del-ref"))
    result = api.delete_order("del-ref")
    assert len(result.deleted_orders) == 1
    assert api.get_order("del-ref") is None


def test_delete_order_not_found_returns_error(api):
    result = api.delete_order(9999)
    assert len(result.deleted_orders) == 0
    assert len(result.errors) == 1
    assert result.errors[0].code == "NOT_FOUND"


def test_delete_orders_batch(api):
    r = api.create_orders([_make_order("d1"), _make_order("d2")])
    ids = [o.order_identifier for o in r.created_orders]
    result = api.delete_orders(ids)
    assert len(result.deleted_orders) == 2
    assert len(result.errors) == 0


def test_delete_orders_partial_not_found(api):
    r = api.create_order(_make_order())
    order_id = r.created_orders[0].order_identifier
    result = api.delete_orders([order_id, 9999])
    assert len(result.deleted_orders) == 1
    assert len(result.errors) == 1


# --- get_label ---


def test_get_label_returns_pdf_bytes(api):
    r = api.create_order(_make_order())
    order_id = r.created_orders[0].order_identifier
    label = api.get_label(order_id, document_type="postageLabel")
    assert isinstance(label, bytearray)
    assert label[:4] == bytearray(b"%PDF")


# --- test_shipping ---


def test_test_shipping_returns_named_tuple(api):
    result = api.test_shipping("smallParcel", "TPN24")
    assert isinstance(result, ShippingTestResult)


def test_test_shipping_succeeds_with_mock(api):
    result = api.test_shipping("smallParcel", "TPN24")
    assert result.is_success is True
    assert isinstance(result.message, str)


def test_test_shipping_cleans_up_order(api):
    api.test_shipping("smallParcel", "TPN24")
    # Mock starts empty and test_shipping deletes its own order — store stays empty.
    assert len(api._orders) == 0


def test_test_shipping_default_weight(api):
    # weight_in_grams defaults to 1 — should not raise
    result = api.test_shipping("letter", "BPL1")
    assert result.is_success is True


def test_test_shipping_address_by_country_code(api):
    result = api.test_shipping("smallParcel", "TPN24", address="DE")
    assert result.is_success is True


def test_test_shipping_address_object(api):
    from click_and_drop_api.simple.addresses import ADDRESSES

    result = api.test_shipping("smallParcel", "TPN24", address=ADDRESSES["FR"])
    assert result.is_success is True


def test_test_shipping_custom_weight(api):
    result = api.test_shipping("smallParcel", "TPN24", weight_in_grams=500)
    assert result.is_success is True


def test_test_shipping_message_is_empty_on_success(api):
    result = api.test_shipping("smallParcel", "TPN24")
    assert result.message == ""


def test_test_shipping_multiple_calls_stay_clean(api):
    for service_code in ("BPL1", "TPN24", "TPS48"):
        result = api.test_shipping("smallParcel", service_code)
        assert result.is_success is True
    assert len(api._orders) == 0


# --- is_oba ---


def test_is_oba_default_is_true():
    assert MockClickAndDrop().is_oba() is True


def test_is_oba_true():
    assert MockClickAndDrop(is_oba=True).is_oba() is True


def test_is_oba_false():
    assert MockClickAndDrop(is_oba=False).is_oba() is False


# --- format_fields_for_error_message ---


def _field(name: str, value: str | None) -> OrderFieldResponse:
    return OrderFieldResponse(fieldName=name, value=value)


def test_format_fields_empty(api):
    assert api.format_fields_for_error_message([]) == ""


def test_format_fields_single(api):
    assert (
        api.format_fields_for_error_message([_field("postcode", "INVALID")])
        == "postcode=INVALID"
    )


def test_format_fields_multiple(api):
    fields = [_field("postcode", "INVALID"), _field("countryCode", "XX")]
    assert (
        api.format_fields_for_error_message(fields)
        == "postcode=INVALID, countryCode=XX"
    )


def test_format_fields_none_value(api):
    assert (
        api.format_fields_for_error_message([_field("postcode", None)])
        == "postcode=None"
    )
