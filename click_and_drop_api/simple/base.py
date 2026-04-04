"""Abstract base class for the Click & Drop API."""

from __future__ import annotations

from abc import ABC, abstractmethod
import os
from typing import Literal, Optional, Self, Union

import click_and_drop_api

import uuid
from datetime import datetime, timezone

from click_and_drop_api.exceptions import ApiException
from click_and_drop_api.models.create_order_response import CreateOrderResponse
from click_and_drop_api.models.order_field_response import OrderFieldResponse
from click_and_drop_api.models.update_order_status_response import (
    UpdateOrderStatusResponse,
)
from click_and_drop_api.models.update_orders_status_request import (
    UpdateOrdersStatusRequest,
)
from click_and_drop_api.simple import (
    Address,
    CreateOrder,
    PostageDetails,
    RecipientDetails,
    ShipmentPackage,
)
from click_and_drop_api.simple.shipping_test_result import ShippingTestResult
from click_and_drop_api.simple.addresses import get_address, get_all_country_codes
from .types import UpdateOrderStatus


class AbstractClickAndDrop(ABC):
    """Common interface shared by ClickAndDrop and MockClickAndDrop."""

    @classmethod
    def from_env(cls, api_env_var: str = "API_KEY") -> Self:
        api_key = os.environ[api_env_var]
        return cls(api_key)

    max_order_count: int = 100

    @property
    @abstractmethod
    def key(self) -> str:
        """The API key in use."""

    @abstractmethod
    def get_version(self) -> click_and_drop_api.GetVersionResource:
        """Get the API version."""

    @abstractmethod
    def _create_orders(
        self, orders: list[CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create one or more orders."""

    def create_orders(
        self, orders: Union[list[CreateOrder], CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a new orders.

        Parameters:
            orders: One or more :class:`~click_and_drop_api.simple.types.CreateOrder` instances.
        Returns:
            A :class:`~click_and_drop_api.models.create_orders_response.CreateOrdersResponse` instance containing created and failed orders.

        https://api.parcel.royalmail.com/#tag/Orders/operation/CreateOrdersAsync
        """
        if isinstance(orders, CreateOrder):
            orders = [orders]
        result = click_and_drop_api.CreateOrdersResponse(
            created_orders=[], failed_orders=[], success_count=0, errors_count=0
        )
        for i in range(0, len(orders), self.max_order_count):
            response = self._create_orders(orders[i : i + self.max_order_count])
            result.created_orders.extend(response.created_orders)
            result.failed_orders.extend(response.failed_orders)
            result.success_count += response.success_count
            result.errors_count += response.errors_count
        return result

    def create_order(
        self, order: CreateOrder
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a single order."""
        return self.create_orders(order)

    @abstractmethod
    def _get_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        """Retrieve orders by identifier or reference."""

    def get_orders(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        """Get specific orders.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.

        Returns:
            A list of orders

        Raises:
            click_and_drop_api.exceptions.BadRequestException if an order with the same reference already exists

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetSpecificOrdersAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = []
        for i in range(0, len(order_identifiers), self.max_order_count):
            result.extend(
                self._get_orders(order_identifiers[i : i + self.max_order_count])
            )
        return result

    def get_order(
        self, order_identifier: Union[str, int]
    ) -> Optional[click_and_drop_api.GetOrderInfoResource]:
        """Retrieve a single order.

        Parameters:
            order_identifier: Order Identifier (integer) or Order Reference (string).

        Returns:
            The order if found, else None.
        """
        orders = self.get_orders(order_identifier)
        return orders[0] if orders else None

    @abstractmethod
    def _delete_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> click_and_drop_api.DeleteOrdersResource:
        """Delete orders by identifier or reference."""

    def delete_orders(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> click_and_drop_api.DeleteOrdersResource:
        """Delete specific orders.

        Please be aware labels generated on orders which are deleted are no longer valid and must be destroyed.
        Cancelled label information is automatically shared with Royal Mail Revenue Protection,
        and should a cancelled label be identified on an item in the Royal Mail Network,
        you will be charged on your account and an additional handling fee applied.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.

        https://api.parcel.royalmail.com/#tag/Orders/operation/DeleteOrdersAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = click_and_drop_api.DeleteOrdersResource(deleted_orders=[], errors=[])
        for i in range(0, len(order_identifiers), self.max_order_count):
            deleted = self._delete_orders(
                order_identifiers[i : i + self.max_order_count]
            )
            result.deleted_orders.extend(deleted.deleted_orders)
            result.errors.extend(deleted.errors)
        return result

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

        Note:
            This method only seems to work for OBA accounts
            to limit the countries.
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
            :class:`~click_and_drop_api.simple.shipping_test_result.ShippingTestResult` with ``success=True/False`` and a message.

        Note:
            This method only seems to work for OBA accounts
            to limit the countries.
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
        try:
            response = self.create_orders(orders)
        except ApiException as e:
            failed_addresses += [get_order_address(order) for order in orders]
            failed_messages += [
                f"API error ({e.status} {e.reason}): {e.body or e.data or ''}"
            ] * len(orders)
        except Exception as e:
            failed_addresses += [get_order_address(order) for order in orders]
            failed_messages += [f"Unexpected error: {e}"] * len(orders)
        for co in response.created_orders:
            successful_addresses.append(get_order_address(co))
            to_delete.append(co.order_identifier)
        for fo in response.failed_orders:
            failed_addresses.append(get_order_address(fo.order))
            failed_messages.append(
                ";".join(
                    f"Error {e.error_code} in "
                    f"{self.format_fields_for_error_message(e.fields)}: "
                    f"{e.error_message}"
                    for e in fo.errors
                )
            )
        self.delete_orders(to_delete)
        return ShippingTestResult(
            successful_addresses, failed_addresses, failed_messages
        )

    def format_fields_for_error_message(self, fields: list[OrderFieldResponse]) -> str:
        """Return a comma-separated list of error message fields."""
        return ", ".join(f"{f.field_name}={f.value}" for f in fields)

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

    def update_order_status(
        self, updates: list[UpdateOrderStatus]
    ) -> UpdateOrderStatusResponse:
        """Set the status of an order.

        Parameters:
            requests: A list of UpdateOrdersStatusRequest instances.

        Returns:
            A :class:`~click_and_drop_api.models.set_order_status_resource.SetOrderStatusResource` instance containing the updated order information.
        """
        result = UpdateOrderStatusResponse(updated_orders=[], errors=[])
        for i in range(0, len(updates), self.max_order_count):
            request = UpdateOrdersStatusRequest(
                items=updates[i : i + self.max_order_count]
            )
            response = self._set_order_status(request)
            result.updated_orders.extend(response.updated_orders)
            result.errors.extend(response.errors)
        return result

    def update_orders(
        self,
        order_identifiers: list[Union[str, int]] | str | int,
        status: Literal["new", "despatchedByOtherCourier", "despatched"] | None = None,
        tracking_number: str | None = None,
        despatch_date: datetime | None = None,
        shipping_carrier: str | None = None,
        shipping_service: str | None = None,
    ):
        """Update the status of multiple orders."""
        return self.update_order_status(
            self._get_orders_update_request(
                order_identifiers,
                status=status,
                tracking_number=tracking_number,
                despatch_date=despatch_date,
                shipping_carrier=shipping_carrier,
                shipping_service=shipping_service,
            )
        )

    def set_order_status(
        self,
        order_identifiers: list[Union[str, int]] | str | int,
        status: Literal["new", "despatchedByOtherCourier", "despatched"],
    ) -> UpdateOrderStatusResponse:
        """Set the status of orders."""
        return self.update_order_status(
            self._get_orders_update_request(order_identifiers, status=status)
        )

    def set_order_tracking_number(
        self, order_identifiers: list[Union[str, int]] | str | int, tracking_number: str
    ) -> UpdateOrderStatusResponse:
        """Set the tracking number of a orders."""
        return self.update_order_status(
            self._get_orders_update_request(
                order_identifiers, tracking_number=tracking_number
            )
        )

    def set_order_despatch_date(
        self,
        order_identifiers: list[Union[str, int]] | str | int,
        despatch_date: datetime,
    ) -> UpdateOrderStatusResponse:
        """Set the despatch date of a orders."""
        return self.update_order_status(
            self._get_orders_update_request(
                order_identifiers, despatch_date=despatch_date
            )
        )

    def set_order_shipping_carrier(
        self,
        order_identifiers: list[Union[str, int]] | str | int,
        shipping_carrier: str,
    ) -> UpdateOrderStatusResponse:
        """Set the shipping carrier of a orders."""
        return self.update_order_status(
            self._get_orders_update_request(
                order_identifiers, shipping_carrier=shipping_carrier
            )
        )

    def set_order_shipping_service(
        self,
        order_identifiers: list[Union[str, int]] | str | int,
        shipping_service: str,
    ) -> UpdateOrderStatusResponse:
        """Set the shipping service of a orders."""
        return self.update_order_status(
            self._get_orders_update_request(
                order_identifiers, shipping_service=shipping_service
            )
        )

    def _get_orders_update_request(
        self,
        order_identifiers: list[Union[str, int]] | str | int,
        status: str | None = None,
        tracking_number: str | None = None,
        despatch_date: datetime | None = None,
        shipping_carrier: str | None = None,
        shipping_service: str | None = None,
    ) -> list[UpdateOrderStatus]:
        """Get a list of UpdateOrderStatus for the given order identifiers and attributes."""
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = []
        for identifier in order_identifiers:
            order_id = identifier if isinstance(identifier, int) else None
            order_ref = identifier if isinstance(identifier, str) else None
            result.append(
                UpdateOrderStatus(
                    order_identifier=order_id,
                    order_reference=order_ref,
                    status=status,
                    tracking_number=tracking_number,
                    despatch_date=despatch_date,
                    shipping_carrier=shipping_carrier,
                    shipping_service=shipping_service,
                )
            )
        return result

    @abstractmethod
    def _set_order_status(
        self, request: UpdateOrdersStatusRequest
    ) -> UpdateOrderStatusResponse:
        """Set the status of an order."""


__all__ = [
    "AbstractClickAndDrop",
]
