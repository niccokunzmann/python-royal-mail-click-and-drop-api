import pytest
from click_and_drop_api.simple import db
from click_and_drop_api.simple.shipping.db import ShippingDB


def _limited(*codes: str) -> ShippingDB:
    return ShippingDB([o for o in db if o.package_size_code in set(codes)])


@pytest.mark.parametrize(
    "weight_grams, expected_package_size",
    [
        (1, "letter"),
        (100, "letter"),
        (101, "largeLetter"),
        (1000, "largeLetter"),
        (1001, "smallParcel"),
        (2000, "smallParcel"),
        (2001, "mediumParcel"),
        (20000, "mediumParcel"),
        (20001, "largeParcel"),
        (30000, "largeParcel"),
    ],
)
def test_filter_weight(weight_grams, expected_package_size):
    result = db.for_weight(weight_grams)
    assert any(o.package_size_code == expected_package_size for o in result)


@pytest.mark.parametrize(
    "weight_grams, expected_package_size",
    [
        (1, "largeLetter"),
        (100, "largeLetter"),
        (101, "largeLetter"),
        (1000, "largeLetter"),
        (1001, "smallParcel"),
        (2000, "smallParcel"),
    ],
)
def test_filter_weight_limited(weight_grams, expected_package_size):
    result = _limited("largeLetter", "smallParcel").for_weight(weight_grams)
    assert any(o.package_size_code == expected_package_size for o in result)


def test_filter_weight_empty():
    assert not db.for_weight(3_000_001)
    assert not _limited("largeLetter", "smallParcel").for_weight(2001)
