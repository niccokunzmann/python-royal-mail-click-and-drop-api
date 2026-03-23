"""Abstract base class for the Click & Drop API."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, NamedTuple, Optional, Union

import click_and_drop_api

import uuid
from datetime import datetime, timezone

from click_and_drop_api.exceptions import ApiException
from click_and_drop_api.models.create_order_response import CreateOrderResponse
from click_and_drop_api.simple import (
    Address,
    CreateOrder,
    PostageDetails,
    RecipientDetails,
    ShipmentPackage,
)
from click_and_drop_api.simple.addresses import get_address, get_all_country_codes


class ShippingTestResult(NamedTuple):
    """Result of a live API shipping test."""

    successful_addresses: list[Address]
    failed_addresses: list[Address]
    failed_messages: list[str]

    @property
    def is_success(self) -> bool:
        """Whether all addresses succeeded.

        Note: If you have several countries to test, this will be ``True`` if
        *any* country succeeds.
        """
        return bool(self.successful_addresses)

    @property
    def is_failure(self) -> bool:
        """Whether any addresses failed.

        Note: If you have several countries to test, this will be ``True`` if
        *any* country failes.
        """
        return bool(self.failed_addresses)

    @property
    def failed_countries(self) -> list[str]:
        """List of ISO 3166-1 alpha-2 country codes that failed."""
        return [a.country_code for a in self.failed_addresses]

    @property
    def successful_countries(self) -> list[str]:
        """List of ISO 3166-1 alpha-2 country codes that succeeded."""
        return [a.country_code for a in self.successful_addresses]


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

    NON_OBA_TEST_SERVICE_CODE = "OLP1"

    def is_oba(self) -> bool:
        """Wether this is an OBA account.

        Check wether this is an OBA account by trying to create an order service code.
        """
        return self.test_shipping("letter", self.NON_OBA_TEST_SERVICE_CODE).is_failure

    def get_countries_for_shipping(
        self,
        package_size: str,
        service_code: str,
        weight_in_grams: int = 1,
    ) -> list[str]:
        """Get a list of ISO 3166-1 alpha-2 country code strings.

        These are the countries that can be shipped with this service.
        """
        countries = get_all_country_codes()
        result = self.test_shipping(
            package_size, service_code, weight_in_grams, countries
        )
        return result.successful_countries

    def test_shipping(
        self,
        package_size: str,
        service_code: str,
        weight_in_grams: int = 1,
        address: Union[str, Address, list[Union[str, Address]]] = "GB",
    ) -> ShippingTestResult:
        """Create a minimal test order, delete it, and report the result.

        Parameters:
            package_size: The package format identifier (e.g. ``"smallParcel"``).
            service_code: The OBA service code to test (e.g. ``"TPN24"``).
            weight_in_grams: Weight of the test parcel in grams. Defaults to 1.
            address: Destination address(es).
                Pass either an :class:`~click_and_drop_api.simple.types.Address`
                instance or an ISO 3166-1 alpha-2 country code string (e.g. ``"DE"``).
                Use :mod:`click_and_drop_api.simple.addresses` for a ready-made
                address for every country.

        Returns:
            :class:`ShippingTestResult` with ``success=True/False`` and a message.
        """
        if not isinstance(address, list):
            address = [address]
        if not address:
            raise ValueError("At least one address or country must be specified")
        address = [get_address(a) if isinstance(a, str) else a for a in address]
        orders = [
            self.create_test_order_for_address(
                package_size, service_code, weight_in_grams, a
            )
            for a in address
        ]
        reference_to_address = {
            order.order_reference: order.recipient.address for order in orders
        }

        def get_order_address(order: CreateOrder | CreateOrderResponse) -> Address:
            return reference_to_address[order.order_reference]

        successful_addresses = []
        failed_addresses = []
        failed_messages = []
        to_delete = []
        # we can request at max 100 orders at a time
        for i in range((len(orders) - 1) // 100 + 1):
            order_subset = orders[i * 100 : (i + 1) * 100]
            try:
                response = self.create_orders(order_subset)
            except ApiException as e:
                failed_addresses += [get_order_address(order) for order in order_subset]
                failed_messages += [
                    f"API error ({e.status} {e.reason}): {e.body or e.data or ''}"
                ] * len(order_subset)
                continue
            except Exception as e:
                failed_addresses += [get_order_address(order) for order in order_subset]
                failed_messages += [f"Unexpected error: {e}"] * len(order_subset)
                continue
            for co in response.created_orders:
                successful_addresses.append(get_order_address(co))
                to_delete.append(co.order_identifier)
            for fo in response.failed_orders:
                failed_addresses.append(get_order_address(fo.order))
                failed_messages.append(
                    ";".join(
                        f"Error {e.error_code} in {e.fields}: {e.error_message}"
                        for e in fo.errors
                    )
                )
        for i in range((len(to_delete) - 1) // 100 + 1):
            self.delete_orders(to_delete[i * 100 : (i + 1) * 100])
        return ShippingTestResult(
            successful_addresses, failed_addresses, failed_messages
        )

    def get_order_test_name(self, country_code: str) -> str:
        """Return a name for a test order for a specific country."""
        return f"test-{country_code}-{uuid.uuid4().hex[:16]}"

    def create_test_order_for_address(
        self,
        package_size: str,
        service_code: str,
        weight_in_grams: int,
        address: Address,
    ):
        """Create an order for a specific country."""

        order_reference = self.get_order_test_name(address.country_code)

        return CreateOrder(
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


__all__ = ["AbstractClickAndDrop", "ShippingTestResult"]
