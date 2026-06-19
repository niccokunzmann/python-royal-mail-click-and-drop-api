"""Tests for MockClickAndDrop.format_fields_for_error_message."""

from click_and_drop_api.models.order_field_response import OrderFieldResponse
from click_and_drop_api.simple.mock import MockClickAndDrop


def _field(name: str, value: str | None) -> OrderFieldResponse:
    return OrderFieldResponse(fieldName=name, value=value)


def test_format_fields_empty(api: MockClickAndDrop):
    assert api.format_fields_for_error_message([]) == ""


def test_format_fields_single(api: MockClickAndDrop):
    assert (
        api.format_fields_for_error_message([_field("postcode", "INVALID")])
        == "postcode=INVALID"
    )


def test_format_fields_multiple(api: MockClickAndDrop):
    fields = [_field("postcode", "INVALID"), _field("countryCode", "XX")]
    assert (
        api.format_fields_for_error_message(fields)
        == "postcode=INVALID, countryCode=XX"
    )


def test_format_fields_none_value(api: MockClickAndDrop):
    assert (
        api.format_fields_for_error_message([_field("postcode", None)])
        == "postcode=None"
    )
