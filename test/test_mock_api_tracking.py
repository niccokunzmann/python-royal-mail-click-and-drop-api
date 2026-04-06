"""Tests for mock tracking number generation on order creation.

Matrix:
    is_oba=True  + tracked service    → tracking number generated
    is_oba=True  + untracked service  → no tracking number
    is_oba=False + tracked service    → tracking number generated
    is_oba=False + untracked service  → no tracking number
"""

from datetime import datetime, timezone

import pytest

from click_and_drop_api.simple.mock import MockClickAndDrop
from click_and_drop_api.simple.types import (
    Address,
    CreateOrder,
    PostageDetails,
    RecipientDetails,
)

# Service codes from ShippingDB (verified via db.for_oba(...))
_SERVICE = {
    (True, True): "SDV",  # OBA,     tracked
    (True, False): "BPL1",  # OBA,     untracked
    (False, True): "SD1OLP",  # non-OBA, tracked
    (False, False): "OLP2",  # non-OBA, untracked
}


def _make_order(reference: str = "ref", service_code: str | None = None) -> CreateOrder:
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
        postage_details=PostageDetails(service_code=service_code)
        if service_code
        else None,
    )


def _create_one(api: MockClickAndDrop, service_code: str | None = None):
    return api.create_order(_make_order(service_code=service_code)).created_orders[0]


# --- matrix: is_oba × tracked ---


@pytest.mark.parametrize("is_oba", [True, False])
@pytest.mark.parametrize("tracked", [True, False])
def test_tracking_number_presence(is_oba: bool, tracked: bool):
    api = MockClickAndDrop(is_oba=is_oba)
    created = _create_one(api, service_code=_SERVICE[is_oba, tracked])
    if tracked:
        assert created.tracking_number is not None
    else:
        assert created.tracking_number is None


@pytest.mark.parametrize("is_oba", [True, False])
def test_tracking_number_format(is_oba: bool):
    api = MockClickAndDrop(is_oba=is_oba)
    created = _create_one(api, service_code=_SERVICE[is_oba, True])
    assert created.tracking_number == f"AB{created.order_identifier:09d}GB"


# --- no postage details ---


def test_no_postage_details_gives_no_tracking():
    api = MockClickAndDrop(is_oba=True)
    created = _create_one(api, service_code=None)
    assert created.tracking_number is None


# --- tracking number persisted on stored order ---


@pytest.mark.parametrize("is_oba", [True, False])
def test_tracking_number_visible_on_get_order(is_oba: bool):
    api = MockClickAndDrop(is_oba=is_oba)
    created = _create_one(api, service_code=_SERVICE[is_oba, True])
    order = api.get_order(created.order_identifier)
    assert order.tracking_number == created.tracking_number


@pytest.mark.parametrize("is_oba", [True, False])
def test_no_tracking_number_on_get_order_for_untracked_service(is_oba: bool):
    api = MockClickAndDrop(is_oba=is_oba)
    created = _create_one(api, service_code=_SERVICE[is_oba, False])
    order = api.get_order(created.order_identifier)
    assert order.tracking_number is None


# --- multiple orders get distinct tracking numbers ---


def test_multiple_orders_get_distinct_tracking_numbers():
    api = MockClickAndDrop(is_oba=True)
    response = api.create_orders(
        [_make_order(f"ref-{i}", _SERVICE[True, True]) for i in range(3)]
    )
    tracking_numbers = [o.tracking_number for o in response.created_orders]
    assert len(set(tracking_numbers)) == 3
