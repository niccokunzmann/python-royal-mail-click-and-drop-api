"""In-memory mock of the ClickAndDrop API for use in tests."""

from __future__ import annotations

import base64
from importlib.resources import files
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Union

import click_and_drop_api

from .base import AbstractClickAndDrop
from .types import CreateOrder
from click_and_drop_api.exceptions import BadRequestException
from click_and_drop_api.models.error_response import ErrorResponse

_MOCK_KEY = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
_MOCK_VERSION = "1.0.0-mock"


class MockClickAndDrop(AbstractClickAndDrop):
    """Drop-in replacement for ClickAndDrop that stores orders in memory.

    Useful for unit tests that should not make real HTTP calls.

    Usage::

        api = MockClickAndDrop()
        response = api.create_order(order)
        assert response.success_count == 1
    """

    def __init__(
        self,
        key: str = _MOCK_KEY,
        is_oba: bool = True,
        despatch_when_manifested: bool = True,
    ):
        """Create a new API object.

        Parameters:
            key: The Click & Drop API authorisation key.
            is_oba: Whether to treat the API as OBA.
            despatch_when_manifested: Whether to despatch orders when they are manifested."""
        if not isinstance(key, str):
            raise TypeError(f"Expected str, got {key}.")
        key = key.strip()
        if not 30 < len(key) < 40:
            raise ValueError(f"Expected 36 characters, got {len(key)}.")
        if "".join(key.split()) != key:
            raise ValueError(f"Expected no whitespace in {key!r}.")
        self._key = key
        self._is_oba = is_oba
        self._orders: dict[int, click_and_drop_api.GetOrderInfoResource] = {}
        self._order_statuses: dict[int, Optional[str]] = {}
        self._next_id = 1
        self._next_manifest_id = 1
        self.despatch_when_manifested = despatch_when_manifested
        self.__now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)

    def _now(self):
        """Update the time."""
        self.__now += timedelta(seconds=1)
        return self.__now

    def is_oba(self) -> bool:
        return self._is_oba

    @property
    def key(self) -> str:
        return self._key

    def get_version(self) -> click_and_drop_api.GetVersionResource:
        return click_and_drop_api.GetVersionResource(
            commit="mock",
            build="mock",
            release=_MOCK_VERSION,
            release_date=self._now(),
        )

    @staticmethod
    def _tracking_number_for(order_id: int) -> str:
        """Generate a mock Royal Mail tracking number embedding the order id.

        The number follows the Royal Mail format (2 letters + 9 digits + 2 letters),
        e.g. ``AB000000001GB``, which can be tracked at::

            https://www.royalmail.com/track-your-item#/tracking-results/AB000000001GB
        """
        return f"AB{order_id:09d}GB"

    def _create_orders(
        self, orders: list[CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        label_count = sum(
            (1 if o.label and o.label.include_label_in_response else 0) for o in orders
        )
        if label_count > 1:
            msg = f"Amount of labels across all items must not exceed '1', was '{label_count}'"
            raise BadRequestException(
                status=400,
                reason="Bad Request",
                body=f'{{"message":"{msg}"}}',
                data=ErrorResponse(message=msg),
            )
        now = self._now()
        created = []
        for order in orders:
            order_id = self._next_id
            self._next_id += 1
            service_code = (
                order.postage_details.service_code
                if order.postage_details is not None
                else None
            )
            service = (
                self.shipping_options.for_service(service_code).any_or_none
                if service_code is not None
                else None
            )
            tracking_number = (
                self._tracking_number_for(order_id)
                if service is not None and service.tracked
                else None
            )
            self._orders[order_id] = click_and_drop_api.GetOrderInfoResource(
                order_identifier=order_id,
                order_reference=order.order_reference,
                created_on=now,
                order_date=order.order_date,
                tracking_number=tracking_number,
            )
            created.append(
                click_and_drop_api.CreateOrderResponse(
                    order_identifier=order_id,
                    order_reference=order.order_reference,
                    created_on=now,
                    order_date=order.order_date,
                    tracking_number=tracking_number,
                )
            )

        return click_and_drop_api.CreateOrdersResponse(
            success_count=len(created),
            errors_count=0,
            created_orders=created,
            failed_orders=[],
        )

    def _get_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = []
        for identifier in order_identifiers:
            if isinstance(identifier, int):
                order = self._orders.get(identifier)
                if order is not None:
                    result.append(order)
            elif isinstance(identifier, str):
                for order in self._orders.values():
                    if order.order_reference == identifier:
                        result.append(order)
                        break
        return result

    def _get_orders_details(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderDetailsResource]:
        postal = click_and_drop_api.GetPostalDetailsResult()
        result = []
        for info in self._get_orders(order_identifiers):
            status = self._order_statuses.get(info.order_identifier)
            result.append(
                click_and_drop_api.GetOrderDetailsResource(
                    order_identifier=info.order_identifier,
                    order_reference=info.order_reference,
                    order_date=info.order_date,
                    created_on=info.created_on,
                    order_status=status,
                    subtotal=0,
                    shipping_cost_charged=0,
                    order_discount=0,
                    total=0,
                    weight_in_grams=0,
                    shipping_details=click_and_drop_api.GetShippingDetailsResult(
                        shipping_cost=0
                    ),
                    shipping_info=postal,
                    billing_info=postal,
                    order_lines=[],
                )
            )
        return result

    def _delete_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> click_and_drop_api.DeleteOrdersResource:
        # TODO: make sure that manifested orders cannot be deleted.
        deleted = []
        errors = []
        for identifier in order_identifiers:
            order = self.get_order(identifier)
            if order is not None:
                del self._orders[order.order_identifier]
                self._order_statuses.pop(order.order_identifier, None)
                deleted.append(
                    click_and_drop_api.DeletedOrderInfo(
                        order_identifier=order.order_identifier,
                        order_reference=order.order_reference,
                    )
                )
            else:
                ref = identifier if isinstance(identifier, str) else None
                id_ = identifier if isinstance(identifier, int) else None
                errors.append(
                    click_and_drop_api.OrderErrorInfo(
                        order_identifier=id_,
                        order_reference=ref,
                        code="NOT_FOUND",
                        message=f"Order {identifier!r} not found.",
                    )
                )

        return click_and_drop_api.DeleteOrdersResource(
            deleted_orders=deleted,
            errors=errors,
        )

    def get_label(
        self,
        order_identifiers: Union[list[Union[str, int]], str, int],
        document_type: Literal["postageLabel", "despatchNote", "CN22", "CN23"],
        include_returns_label: Optional[bool] = None,
        include_cn: Optional[bool] = None,
    ) -> bytearray:
        orders = self._get_orders(order_identifiers)
        for order in orders:
            order.printed_on = self._now()
        labels_file = "mock-label-cn.pdf" if include_cn else "mock-label.pdf"
        data = files("click_and_drop_api.examples").joinpath(labels_file).read_bytes()
        return bytearray(data)

    def _manifest_orders(
        self, request: click_and_drop_api.ManifestEligibleOrdersRequest
    ) -> click_and_drop_api.ManifestOrdersResponse:
        for order in self._orders.values():
            if not order.printed_on:
                order.printed_on = self._now()
            order.manifested_on = self._now()
            if self.despatch_when_manifested:
                order.shipped_on = self._now()
        manifest_id = self._next_manifest_id
        self._next_manifest_id += 1
        data = (
            files("click_and_drop_api.examples")
            .joinpath("mock-manifest.pdf")
            .read_bytes()
        )
        return click_and_drop_api.ManifestOrdersResponse(
            manifest_number=manifest_id,
            document_pdf=base64.b64encode(data).decode(),
        )

    def _set_order_status(
        self, request: click_and_drop_api.UpdateOrdersStatusRequest
    ) -> click_and_drop_api.UpdateOrderStatusResponse:
        updated = []
        errors = []
        for item in request.items or []:
            order = self.get_order(
                item.order_identifier
                if item.order_identifier is not None
                else item.order_reference
            )
            if order is not None and item.status is not None:
                self._order_statuses[order.order_identifier] = item.status
                order = self._get_orders(
                    order.order_identifier or order.order_reference
                )[0]
                order.shipped_on = self._now()
            updated.append(
                click_and_drop_api.UpdatedOrderInfo(
                    order_identifier=item.order_identifier,
                    order_reference=item.order_reference,
                    status=item.status,
                )
            )

        return click_and_drop_api.UpdateOrderStatusResponse(
            updated_orders=updated,
            errors=errors,
        )


__all__ = ["MockClickAndDrop"]
