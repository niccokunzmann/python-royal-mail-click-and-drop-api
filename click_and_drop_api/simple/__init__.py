"""Simple API access based on the generated API interface."""

from .types import CreateOrder, RecipientDetails, Address
from .api import ClickAndDrop
from .package_sizes import PackageSize, packages_sizes, get_package_size
from .shipping_options import ShippingOption, add_shipping_option, shipping_options


__all__ = [
    "ClickAndDrop",
    "CreateOrder",
    "RecipientDetails",
    "Address",
    "PackageSize",
    "packages_sizes",
    "ShippingOption",
    "add_shipping_option",
    "shipping_options",
    "get_package_size",
]
