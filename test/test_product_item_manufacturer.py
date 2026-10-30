"""Manufacturer fields of ProductItem, required by Royal Mail for EU shipments."""

import pytest
from pydantic import ValidationError

from click_and_drop_api.simple import ProductItem


def test_non_standardised_manufacturer_id_is_sent():
    item = ProductItem(quantity=1, non_standardised_manufacturer_id="MYCO-TTE-60")
    assert item.to_dict()["NonStandardisedManufacturerId"] == "MYCO-TTE-60"


def test_standardised_manufacturer_id_is_sent():
    item = ProductItem(quantity=1, standardised_manufacturer_id="5012345678900")
    assert item.to_dict()["StandardisedManufacturerId"] == "5012345678900"


def test_pga_reference_number_is_sent():
    item = ProductItem(quantity=1, pga_reference_number="PGA-1")
    assert item.to_dict()["PgaReferenceNumber"] == "PGA-1"


def test_manufacturer_ids_are_left_out_when_not_set():
    data = ProductItem(quantity=1).to_dict()
    assert "NonStandardisedManufacturerId" not in data
    assert "StandardisedManufacturerId" not in data


def test_manufacturer_id_is_read_from_api_json():
    item = ProductItem.from_dict(
        {"quantity": 1, "NonStandardisedManufacturerId": "MYCO-TTE-60"}
    )
    assert item.non_standardised_manufacturer_id == "MYCO-TTE-60"


def test_manufacturer_id_max_length_is_50():
    with pytest.raises(ValidationError):
        ProductItem(quantity=1, non_standardised_manufacturer_id="x" * 51)


def test_customs_description_allows_255_characters():
    item = ProductItem(quantity=1, customs_description="x" * 255)
    assert len(item.customs_description) == 255
