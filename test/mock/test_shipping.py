"""Tests for MockClickAndDrop.test_shipping."""

from click_and_drop_api.simple.mock import MockClickAndDrop
from click_and_drop_api.simple.shipping_test_result import ShippingTestResult


def test_test_shipping_returns_named_tuple(api: MockClickAndDrop):
    result = api.test_shipping("smallParcel", "TPN24")
    assert isinstance(result, ShippingTestResult)


def test_test_shipping_succeeds_with_mock(api: MockClickAndDrop):
    result = api.test_shipping("smallParcel", "TPN24")
    assert result.is_success is True
    assert isinstance(result.message, str)


def test_test_shipping_cleans_up_order(api: MockClickAndDrop):
    api.test_shipping("smallParcel", "TPN24")
    assert len(api._orders) == 0


def test_test_shipping_default_weight(api: MockClickAndDrop):
    result = api.test_shipping("letter", "BPL1")
    assert result.is_success is True


def test_test_shipping_address_by_country_code(api: MockClickAndDrop):
    result = api.test_shipping("smallParcel", "TPN24", address="DE")
    assert result.is_success is True


def test_test_shipping_address_object(api: MockClickAndDrop):
    from click_and_drop_api.simple.addresses import ADDRESSES

    result = api.test_shipping("smallParcel", "TPN24", address=ADDRESSES["FR"])
    assert result.is_success is True


def test_test_shipping_custom_weight(api: MockClickAndDrop):
    result = api.test_shipping("smallParcel", "TPN24", weight_in_grams=500)
    assert result.is_success is True


def test_test_shipping_message_is_empty_on_success(api: MockClickAndDrop):
    result = api.test_shipping("smallParcel", "TPN24")
    assert result.message == ""


def test_test_shipping_multiple_calls_stay_clean(api: MockClickAndDrop):
    for service_code in ("BPL1", "TPN24", "TPS48"):
        result = api.test_shipping("smallParcel", service_code)
        assert result.is_success is True
    assert len(api._orders) == 0
