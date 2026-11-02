"""MockClickAndDrop rejects EU items without a manufacturer ID, like Royal Mail (error 119)."""

from datetime import datetime, timezone

import pytest

from click_and_drop_api import ShipmentPackageRequest
from click_and_drop_api.simple.mock import MockClickAndDrop
from click_and_drop_api.simple.types import (
    Address,
    CreateOrder,
    ProductItem,
    RecipientDetails,
)


def make_order(country_code: str, *items: ProductItem, reference="ref-1") -> CreateOrder:
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
                address_line1="Strøget 1",
                city="Copenhagen",
                postcode="2000",
                country_code=country_code,
            )
        ),
        packages=[
            ShipmentPackageRequest(
                weight_in_grams=100,
                package_format_identifier="largeLetter",
                contents=list(items) or None,
            )
        ],
    )


def item(**kwargs) -> ProductItem:
    return ProductItem(quantity=1, unit_value=10.0, unit_weight_in_grams=50, **kwargs)


@pytest.mark.parametrize("country_code", ["DK", "DE", "IE", "FR"])
def test_eu_item_without_manufacturer_id_fails(api: MockClickAndDrop, country_code):
    response = api.create_order(make_order(country_code, item()))
    assert response.success_count == 0
    assert response.errors_count == 1
    assert response.created_orders == []
    [failed] = response.failed_orders
    assert failed.order.order_reference == "ref-1"
    [error] = failed.errors
    assert error.error_code == 119
    assert "EU or USA" in error.error_message
    assert error.fields[0].field_name == "Packages.Contents.NonStandardisedManufacturerId"


def test_failed_order_is_not_stored(api: MockClickAndDrop):
    api.create_order(make_order("DK", item()))
    assert api.lookup_references(["ref-1"]).absent == {"ref-1"}


def test_one_error_per_item_without_manufacturer_id(api: MockClickAndDrop):
    response = api.create_order(
        make_order("DK", item(), item(non_standardised_manufacturer_id="M1"), item())
    )
    assert len(response.failed_orders[0].errors) == 2


@pytest.mark.parametrize(
    "kwargs",
    [
        {"non_standardised_manufacturer_id": "MYCO-1"},
        {"standardised_manufacturer_id": "5012345678900"},
        {"customs_declaration_category": "gift"},
        {"customs_declaration_category": "documents"},
    ],
)
def test_eu_item_succeeds(api: MockClickAndDrop, kwargs):
    response = api.create_order(make_order("DK", item(**kwargs)))
    assert response.success_count == 1
    assert response.failed_orders == []


@pytest.mark.parametrize(
    "category", [None, "commercialSaleOfGoods", "eCommerceSaleOfGoods"]
)
def test_sale_of_goods_needs_manufacturer_id(api: MockClickAndDrop, category):
    response = api.create_order(
        make_order("DK", item(customs_declaration_category=category))
    )
    assert response.errors_count == 1


@pytest.mark.parametrize("country_code", ["GB", "US", "CH", "NO"])
def test_non_eu_item_without_manufacturer_id_succeeds(api: MockClickAndDrop, country_code):
    response = api.create_order(make_order(country_code, item()))
    assert response.success_count == 1


def test_eu_order_without_contents_succeeds(api: MockClickAndDrop):
    response = api.create_order(make_order("DK"))
    assert response.success_count == 1


def test_only_the_invalid_order_fails_in_a_batch(api: MockClickAndDrop):
    response = api.create_orders(
        [
            make_order("DK", item(), reference="bad"),
            make_order("DK", item(non_standardised_manufacturer_id="M1"), reference="good"),
        ]
    )
    assert [o.order_reference for o in response.created_orders] == ["good"]
    assert [o.order.order_reference for o in response.failed_orders] == ["bad"]
    assert response.success_count == 1
    assert response.errors_count == 1
