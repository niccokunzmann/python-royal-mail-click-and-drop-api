"""Simple API access based on the generated API interface."""

from .types import (
    Address,
    BillingDetails,
    CreateOrder,
    CreateOrders,
    Dimensions,
    LabelGeneration,
    ManifestDetailsResponse,
    ManifestEligibleOrders,
    PostageDetails,
    ProductItem,
    RecipientDetails,
    SenderDetails,
    ShipmentPackage,
    Tag,
    UpdateOrderStatus,
    UpdateOrderStatusResponse,
    UpdateOrdersStatus,
    ManifestedOrders,
    OrderInfo,
)
from .api import ClickAndDrop
from .mock import MockClickAndDrop
from .shipping.db import (
    ShippingDB,
    PackageShippingOption,
    db,
)
from .shipping import check_service_codes
from .errors import InvalidWeight, InvalidDimensions

__all__ = [
    "ClickAndDrop",
    "MockClickAndDrop",
    "CreateOrder",
    "InvalidWeight",
    "InvalidDimensions",
    "check_service_codes",
    "RecipientDetails",
    "Address",
    "ShippingDB",
    "PackageShippingOption",
    "db",
    "CreateOrders",
    "UpdateOrdersStatus",
    "UpdateOrderStatus",
    "UpdateOrderStatusResponse",
    "LabelGeneration",
    "OrderInfo",
    "ManifestedOrders",
    "ManifestEligibleOrders",
    "ManifestDetailsResponse",
    "PostageDetails",
    "ProductItem",
    "SenderDetails",
    "ShipmentPackage",
    "Tag",
    "Dimensions",
    "BillingDetails",
]
