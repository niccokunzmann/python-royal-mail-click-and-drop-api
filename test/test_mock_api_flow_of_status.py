"""Test the different statuses in the mock api."""

from typing import Callable

from click_and_drop_api.simple.mock import MockClickAndDrop
import pytest
from datetime import datetime, timezone
from click_and_drop_api.simple.types import (
    CreateOrder,
    OrderInfo,
    RecipientDetails,
    Address,
)


UTC = timezone.utc
S = OrderInfo.STATUS


@pytest.fixture
def api():
    return MockClickAndDrop()


@pytest.fixture
def order(api: MockClickAndDrop):
    """Create an order."""
    # choose a new reference or else the API will reject the order
    REFERENCE = "example-order-{now}".format(
        now=datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    )

    service = api.shipping_options.any

    new_order = CreateOrder(
        order_reference=REFERENCE,
        is_recipient_a_business=False,
        recipient=RecipientDetails(
            address=Address(
                full_name="Nicco Kunzmann",
                company_name="",
                address_line1="Wernlas",
                address_line2="Talley",
                address_line3="",
                city="Llandeilo",
                county="United Kingdom",
                postcode="SA19 7EE",
                country_code="GB",
            ),
            phone_number="07726640000",
            email_address="niccokunzmann" + "@" + "rambler.ru",
        ),
        order_date=datetime.now(UTC),
        subtotal=float(12),  # 12 pounds
        shipping_cost_charged=float(service.gross),  # charge the same as Royal Mail
        total=float(12 + service.gross),
        currency_code="GBP",
        postage_details=service.as_postage_details(),
        packages=[service.as_package_request(weight_in_grams=80)],
        ## Label generation is only possible for OBA customers
        # label=LabelGeneration(
        #     include_label_in_response=True,
        #     include_cn=False,
        #     include_returns_label=False,
        # ),
    )
    api.create_order(new_order)

    return new_order


@pytest.fixture
def order_info(api: MockClickAndDrop, order: CreateOrder) -> Callable[[], OrderInfo]:
    """Retrieve the order information from the API."""

    def get() -> OrderInfo:
        return api.get_order(order.order_reference)

    return get


def test_new_order_has_status_new(order_info: Callable[[], OrderInfo]):
    """A new order only has the new status."""
    assert order_info().status_history == [S.NEW]


def test_generating_a_label_changes_status_to_label_generated(
    order_info: Callable[[], OrderInfo], api: MockClickAndDrop
):
    """Generating a label changes the status to label generated."""
    api.get_label(order_info().order_reference, document_type="postageLabel")
    assert order_info().status_history == [S.NEW, S.LABEL_GENERATED]


def test_manifesting_an_order_with_postage_changes_status_to_manifested(
    order_info: Callable[[], OrderInfo], api: MockClickAndDrop
):
    """Manifesting an order with postage changes the status to manifested."""
    api.despatch_when_manifested = True
    api.manifest_orders()
    assert order_info().status_history == [
        S.NEW,
        S.LABEL_GENERATED,
        S.MANIFESTED,
        S.DESPATCHED,
    ]


def test_when_not_despatching_instantly_the_order_is_not_despatched(
    order_info: Callable[[], OrderInfo], api: MockClickAndDrop
):
    """When not despatching instantly, the order is not despatched."""
    api.despatch_when_manifested = False
    api.manifest_orders()
    assert order_info().status_history == [S.NEW, S.LABEL_GENERATED, S.MANIFESTED]


@pytest.mark.parametrize(
    "status",
    [
        "despatched",
        "despatchedByOtherCourier",
    ],
)
@pytest.mark.parametrize("manifest", [True, False])
def test_setting_an_order_as_despatched_changes_status_to_despatched(
    order_info: Callable[[], OrderInfo], api: MockClickAndDrop, status, manifest
):
    """Setting an order as despatched changes the status to despatched."""
    if manifest:
        api.despatch_when_manifested = False
        api.manifest_orders()
    api.set_order_status(order_info().order_reference, status)
    assert S.DESPATCHED in order_info().status_history
