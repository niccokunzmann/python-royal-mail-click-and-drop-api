"""Abstract base class for the Click & Drop API."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, NamedTuple, Optional, Union

import click_and_drop_api

import uuid
from datetime import datetime, timezone

from click_and_drop_api.exceptions import ApiException
from click_and_drop_api.simple import (
    Address,
    CreateOrder,
    PostageDetails,
    RecipientDetails,
    ShipmentPackage,
)
from click_and_drop_api.simple.addresses import get_address


class ShippingTestResult(NamedTuple):
    """Result of a live API shipping test."""

    success: bool
    message: str


class AbstractClickAndDrop(ABC):
    """Common interface shared by ClickAndDrop and MockClickAndDrop."""

    @property
    @abstractmethod
    def key(self) -> str:
        """The API key in use."""

    @abstractmethod
    def get_version(self) -> click_and_drop_api.GetVersionResource:
        """Get the API version."""

    @abstractmethod
    def create_orders(
        self, orders: Union[list[CreateOrder], CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create one or more orders."""

    def create_order(
        self, order: CreateOrder
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a single order."""
        return self.create_orders(order)

    @abstractmethod
    def get_orders(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        """Retrieve orders by identifier or reference."""

    def get_order(
        self, order_identifier: Union[str, int]
    ) -> Optional[click_and_drop_api.GetOrderInfoResource]:
        """Retrieve a single order, or None if not found."""
        orders = self.get_orders(order_identifier)
        return orders[0] if orders else None

    @abstractmethod
    def delete_orders(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> click_and_drop_api.DeleteOrdersResource:
        """Delete orders by identifier or reference."""

    def delete_order(
        self, order_identifier: Union[str, int]
    ) -> click_and_drop_api.DeleteOrdersResource:
        """Delete a single order."""
        return self.delete_orders(order_identifier)

    @abstractmethod
    def get_label(
        self,
        order_identifiers: Union[list[Union[str, int]], str, int],
        document_type: Literal["postageLabel", "despatchNote", "CN22", "CN23"],
        include_returns_label: Optional[bool] = None,
        include_cn: Optional[bool] = None,
    ) -> bytearray:
        """Generate a label PDF for one or more orders."""

    def test_shipping(
        self,
        package_size: str,
        service_code: str,
        weight_in_grams: int = 1,
        address: "Union[str, Address]" = "GB",
    ) -> ShippingTestResult:
        """Create a minimal test order, delete it, and report the result.

        Parameters:
            package_size: The package format identifier (e.g. ``"smallParcel"``).
            service_code: The OBA service code to test (e.g. ``"TPN24"``).
            weight_in_grams: Weight of the test parcel in grams. Defaults to 1.
            address: Destination address. Pass either an :class:`~click_and_drop_api.simple.types.Address`
                instance or an ISO 3166-1 alpha-2 country code string (e.g. ``"DE"``).
                Use :mod:`click_and_drop_api.simple.addresses` for a ready-made
                address for every country.

        Returns:
            :class:`ShippingTestResult` with ``success=True/False`` and a message.
        """

        if isinstance(address, str):
            address = get_address(address)

        order_reference = f"test-{uuid.uuid4().hex[:16]}"

        order = CreateOrder(
            order_reference=order_reference,
            recipient=RecipientDetails(address=address),
            packages=[
                ShipmentPackage(
                    weight_in_grams=weight_in_grams,
                    package_format_identifier=package_size,
                )
            ],
            order_date=datetime.now(timezone.utc),
            subtotal=1.00,
            shipping_cost_charged=0.00,
            total=1.00,
            currency_code="GBP",
            postage_details=PostageDetails(service_code=service_code),
        )

        try:
            response = self.create_order(order)
        except ApiException as e:
            return ShippingTestResult(
                False, f"API error ({e.status} {e.reason}): {e.body or e.data or ''}"
            )
        except Exception as e:
            return ShippingTestResult(False, f"Unexpected error: {e}")

        if response.failed_orders:
            errors = [
                e2.error_message
                for e1 in response.failed_orders
                for e2 in (e1.errors or [])
                if e2.error_message
            ]
            return ShippingTestResult(
                False,
                f"Order rejected by API: {'; '.join(errors) or response.failed_orders}",
            )

        if response.created_orders:
            order_ids = [co.order_identifier for co in response.created_orders]
            try:
                self.delete_orders(order_ids)
            except ApiException:
                pass  # best-effort cleanup
            return ShippingTestResult(
                True,
                (
                    f"API accepted the order (id {order_ids[0]}) "
                    f"and it was deleted immediately."
                ),
            )

        return ShippingTestResult(
            False, "API returned no created orders and no errors — unexpected response."
        )


__all__ = ["AbstractClickAndDrop", "ShippingTestResult"]
