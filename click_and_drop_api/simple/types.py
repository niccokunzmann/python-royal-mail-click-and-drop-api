"""Renamed types for nicer reading"""

from click_and_drop_api.models.address_request import AddressRequest as Address
from click_and_drop_api.models.billing_details_request import (
    BillingDetailsRequest as BillingDetails,
)
from click_and_drop_api.models.create_order_request import (
    CreateOrderRequest as CreateOrder,
)
from click_and_drop_api.models.create_orders_request import (
    CreateOrdersRequest as CreateOrders,
)
from click_and_drop_api.models.dimensions_request import DimensionsRequest as Dimensions
from click_and_drop_api.models.label_generation_request import (
    LabelGenerationRequest as LabelGeneration,
)
from click_and_drop_api.models.manifest_details_response import (
    ManifestDetailsResponse as ManifestDetailsResponse,
)
from click_and_drop_api.models.manifest_eligible_orders_request import (
    ManifestEligibleOrdersRequest as ManifestEligibleOrders,
)
from click_and_drop_api.models.postage_details_request import (
    PostageDetailsRequest as PostageDetails,
)
from click_and_drop_api.models.product_item_request import (
    ProductItemRequest as ProductItem,
)
from click_and_drop_api.models.recipient_details_request import (
    RecipientDetailsRequest as RecipientDetails,
)
from click_and_drop_api.models.sender_details_request import (
    SenderDetailsRequest as SenderDetails,
)
from click_and_drop_api.models.shipment_package_request import (
    ShipmentPackageRequest as ShipmentPackage,
)
from click_and_drop_api.models.tag_request import TagRequest as Tag
from click_and_drop_api.models.update_order_status_request import (
    UpdateOrderStatusRequest as UpdateOrderStatus,
)
from click_and_drop_api.models.update_order_status_response import (
    UpdateOrderStatusResponse as UpdateOrderStatusResponse,
)
from click_and_drop_api.models.update_orders_status_request import (
    UpdateOrdersStatusRequest as UpdateOrdersStatus,
)


__all__ = [
    "CreateOrder",
    "RecipientDetails",
    "Address",
    "PostageDetails",
    "ShipmentPackage",
    "CreateOrders",
    "BillingDetails",
    "Dimensions",
    "LabelGeneration",
    "ProductItem",
    "UpdateOrderStatus",
    "UpdateOrdersStatus",
    "Tag",
    "UpdateOrderStatusResponse",
    "ManifestDetailsResponse",
    "ManifestEligibleOrders",
    "SenderDetails",
]
