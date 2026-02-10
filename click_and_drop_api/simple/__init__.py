"""Simple API access based on the generated API interface."""

from .types import CreateOrder, RecipientDetails, Address
from .api import ClickAndDrop
from .package_sizes import (
    PackageSize,
    packages_sizes,
    get_package_size,
    choose_package_size_by_weight,
    get_package_sizes,
)
from .shipping_options import (
    ShippingOption,
    add_shipping_option,
    shipping_options,
    list_service_codes,
    check_service_codes,
)


__all__ = [
    "ClickAndDrop",
    "CreateOrder",
    "check_service_codes",
    "RecipientDetails",
    "list_service_codes",
    "Address",
    "get_package_sizes",
    "PackageSize",
    "packages_sizes",
    "ShippingOption",
    "add_shipping_option",
    "shipping_options",
    "choose_package_size_by_weight",
    "get_package_size",
]
