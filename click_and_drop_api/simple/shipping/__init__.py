"""Shipping options with prices.

These shipping options are copied from the website to create a database.

"""

from typing import Sequence

from .package_shipping_option import PackageShippingOption

from . import letter
from . import large_letter
from . import small_parcel
from . import medium_parcel
from . import large_parcel
from . import parcel
from . import documents


def _get_all_shipping_options() -> list[PackageShippingOption]:
    return (
        letter.options
        + large_letter.options
        + small_parcel.options
        + medium_parcel.options
        + large_parcel.options
        + parcel.options
        + documents.options
    )


def list_service_codes() -> list[str]:
    """All shipping option service codes."""
    return list({option.service_code for option in _get_all_shipping_options()})


def check_service_codes(service_codes: Sequence[str]):
    """Check if all service codes are valid."""
    all_service_codes = list_service_codes()
    for service_code in service_codes:
        if service_code not in all_service_codes:
            raise ValueError(
                f"Invalid service code: {service_code}. Should be one of {', '.join(list_service_codes())}"
            )


def get_shipping_options(*codes: str) -> list[PackageShippingOption]:
    """Return the shipping options with the given service codes."""
    code_set = set(codes)
    return [
        option
        for option in _get_all_shipping_options()
        if option.service_code in code_set
    ]


__all__ = [
    "PackageShippingOption",
    "documents",
    "large_letter",
    "large_parcel",
    "letter",
    "medium_parcel",
    "parcel",
    "small_parcel",
]
