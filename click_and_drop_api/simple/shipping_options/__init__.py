"""Shipping options with prices.

These shipping options are copied from the website to create a database.

"""

from typing import Sequence

from .model import ShippingOption

from . import letter
from . import large_letter
from . import small_parcel
from . import medium_parcel
from . import large_parcel


def _get_all_shipping_options() -> list[ShippingOption]:
    return (
        letter.options
        + large_letter.options
        + small_parcel.options
        + medium_parcel.options
        + large_parcel.options
    )


def list_service_codes() -> list[str]:
    """All shipping option service codes."""
    return list(
        {
            shipping_option.service_code
            for shipping_option in _get_all_shipping_options()
        }
    )


def check_service_codes(service_codes: Sequence[str]):
    """Check if all service codes are valid."""
    all_service_codes = list_service_codes()
    for service_code in service_codes:
        if service_code not in all_service_codes:
            raise ValueError(
                f"Invalid service code: {service_code}. Should be one of {', '.join(list_service_codes())}"
            )


def get_shipping_options(*options: str) -> list[ShippingOption]:
    """Return the shipping options with the codes."""
    options = set(options)
    return [
        shipping_option
        for shipping_option in _get_all_shipping_options()
        if shipping_option.service_code in options
    ]


__all__ = [
    "large_letter",
    "large_parcel",
    "letter",
    "medium_parcel",
    "small_parcel",
]
