"""Tests for MockClickAndDrop.create_order / create_orders."""

import pytest

from click_and_drop_api.exceptions import BadRequestException
from click_and_drop_api.simple.mock import MockClickAndDrop
from click_and_drop_api.simple.types import LabelGeneration

from .helpers import make_order


def _make_order_with_label(reference: str, include_returns_label: bool = False):
    from datetime import datetime, timezone
    from click_and_drop_api.simple.types import Address, CreateOrder, RecipientDetails

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
        label=LabelGeneration(
            include_label_in_response=True,
            include_returns_label=include_returns_label,
        ),
    )


def test_create_order_single(api: MockClickAndDrop):
    response = api.create_order(make_order())
    assert response.success_count == 1
    assert response.errors_count == 0
    assert len(response.created_orders) == 1
    assert len(response.failed_orders) == 0


def test_create_orders_batch(api: MockClickAndDrop):
    response = api.create_orders([make_order("ref-a"), make_order("ref-b")])
    assert response.success_count == 2
    assert len(response.created_orders) == 2


def test_created_order_has_correct_reference(api: MockClickAndDrop):
    response = api.create_order(make_order("my-ref"))
    assert response.created_orders[0].order_reference == "my-ref"


def test_created_order_has_integer_identifier(api: MockClickAndDrop):
    response = api.create_order(make_order())
    assert isinstance(response.created_orders[0].order_identifier, int)


def test_order_identifiers_increment(api: MockClickAndDrop):
    r1 = api.create_order(make_order("ref-1"))
    r2 = api.create_order(make_order("ref-2"))
    id1 = r1.created_orders[0].order_identifier
    id2 = r2.created_orders[0].order_identifier
    assert id2 == id1 + 1


# --- label count validation ---


def test_single_label_request_succeeds():
    api = MockClickAndDrop()
    response = api.create_order(_make_order_with_label("ref-label-1"))
    assert response.success_count == 1


def test_two_orders_with_labels_raises_bad_request():
    api = MockClickAndDrop()
    with pytest.raises(BadRequestException) as exc_info:
        api.create_orders(
            [
                _make_order_with_label("ref-label-2a"),
                _make_order_with_label("ref-label-2b"),
            ]
        )
    assert "Amount of labels across all items must not exceed '1', was '2'" in str(
        exc_info.value
    )


def test_label_and_returns_label_succeeds():
    api = MockClickAndDrop()
    response = api.create_order(
        _make_order_with_label("ref-label-3", include_returns_label=True)
    )
    assert response.success_count == 1
