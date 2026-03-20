"""Tests for ShippingOption.enhancement property and parser."""

from decimal import Decimal as D

import pytest

from click_and_drop_api.simple.shipping_options.model import ShippingOption
from click_and_drop_api.simple.shipping_options.letter import options as letter_options
from click_and_drop_api.simple.shipping_options.large_letter import (
    options as large_letter_options,
)
from click_and_drop_api.simple.shipping_options.small_parcel import (
    options as small_parcel_options,
)
from click_and_drop_api.simple.shipping_options.large_parcel import (
    options as large_parcel_options,
)


def _make(**kwargs) -> ShippingOption:
    defaults = dict(
        package_size="letter",
        brand="Royal Mail",
        service="Test Service (£20 compensation)",
        service_code="OLP1",
        delivery_speed="24 hour",
        compensation=D("20.00"),
        gross=D("1.70"),
    )
    defaults.update(kwargs)
    return ShippingOption(**defaults)


# --- enhancement property ---


@pytest.mark.parametrize(
    "flags,expected",
    [
        ({}, ""),
        ({"tracked": True}, "Tracked"),
        (
            {"tracked": True, "email_notification": True, "sms_notification": True},
            "Tracked, Email notification, SMS notification",
        ),
        (
            {
                "tracked": True,
                "email_notification": True,
                "sms_notification": True,
                "safeplace": True,
            },
            "Tracked, Email notification, SMS notification, Safeplace",
        ),
        (
            {
                "tracked": True,
                "email_notification": True,
                "sms_notification": True,
                "age_verified": True,
            },
            "Tracked, Email notification, SMS notification, Age verified on delivery",
        ),
        ({"ioss": True}, "IOSS"),
        ({"tracked": True, "ioss": True}, "Tracked, IOSS"),
        (
            {
                "tracked": True,
                "email_notification": True,
                "sms_notification": True,
                "safeplace": True,
                "age_verified": True,
                "ioss": True,
            },
            "Tracked, Email notification, SMS notification, Safeplace, Age verified on delivery, IOSS",
        ),
    ],
)
def test_enhancement(flags, expected):
    assert _make(**flags).enhancement == expected


# --- parser ---


def test_letter_returns_options():
    assert len(letter_options) > 0


def test_letter_gb_domestic():
    assert any(not o.international for o in letter_options)


def test_letter_de_international():
    assert any(o.international for o in letter_options)


def test_tracked_flags_parsed():
    assert any(o.tracked for o in letter_options)


def test_safeplace_flag():
    assert any(o.safeplace for o in large_letter_options)


def test_ioss_flag_international():
    assert any(o.ioss for o in letter_options)


def test_compensation_parsed():
    olp1 = next(
        o for o in letter_options if o.service_code == "OLP1" and not o.international
    )
    assert olp1.compensation == D("20.00")


def test_gross_and_tax_parsed():
    tolp24 = next(o for o in large_letter_options if o.service_code == "TOLP24")
    assert tolp24.gross == D("3.65")
    assert tolp24.tax == D("0.61")
    assert tolp24.net == D("3.04")


def test_brand_royal_mail():
    domestic_non_oba = [
        o for o in letter_options if not o.international and not o.is_oba
    ]
    assert all(o.brand == "Royal Mail" for o in domestic_non_oba)


def test_brand_parcel_force():
    assert any(o.brand == "Parcel Force" for o in large_parcel_options)


def test_package_size_stored():
    assert all(o.package_size == "smallParcel" for o in small_parcel_options)


def test_enhancement_roundtrip():
    tolp24 = next(o for o in large_letter_options if o.service_code == "TOLP24")
    assert tolp24.tracked is True
    assert tolp24.email_notification is True
    assert tolp24.sms_notification is True
    assert tolp24.safeplace is True
    assert (
        tolp24.enhancement == "Tracked, Email notification, SMS notification, Safeplace"
    )


# --- ships_to ---


@pytest.mark.parametrize(
    "international,country_code,expected",
    [
        (False, "GB", True),
        (False, "DE", False),
        (True, "DE", True),
        (True, "GB", False),
    ],
)
def test_ships_to(international, country_code, expected):
    assert _make(international=international).ships_to(country_code) is expected


@pytest.mark.parametrize("code", ["GBR", "", "G"])
def test_ships_to_invalid_country_code(code):
    with pytest.raises(ValueError):
        _make().ships_to(code)
