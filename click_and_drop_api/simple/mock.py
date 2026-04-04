"""In-memory mock of the ClickAndDrop API for use in tests."""

from __future__ import annotations

import base64
from importlib.resources import files
from datetime import datetime, timezone
from typing import Literal, Optional, Union

import click_and_drop_api

from .base import AbstractClickAndDrop
from .types import CreateOrder

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

    def __init__(self, key: str = _MOCK_KEY, is_oba: bool = True):
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
        self._next_id = 1
        self._next_manifest_id = 1

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
            release_date=datetime.now(timezone.utc),
        )

    def _create_orders(
        self, orders: list[CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        now = datetime.now(timezone.utc)
        created = []
        for order in orders:
            order_id = self._next_id
            self._next_id += 1
            self._orders[order_id] = click_and_drop_api.GetOrderInfoResource(
                order_identifier=order_id,
                order_reference=order.order_reference,
                created_on=now,
                order_date=order.order_date,
            )
            created.append(
                click_and_drop_api.CreateOrderResponse(
                    order_identifier=order_id,
                    order_reference=order.order_reference,
                    created_on=now,
                    order_date=order.order_date,
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

    def _delete_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> click_and_drop_api.DeleteOrdersResource:
        deleted = []
        errors = []
        for identifier in order_identifiers:
            order = self.get_order(identifier)
            if order is not None:
                del self._orders[order.order_identifier]
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
        data = (
            files("click_and_drop_api.examples").joinpath("mock-label.pdf").read_bytes()
        )
        return bytearray(data)

    def _manifest_orders(
        self, request: click_and_drop_api.ManifestEligibleOrdersRequest
    ) -> click_and_drop_api.ManifestOrdersResponse:
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
        # For simplicity, this mock does not actually update the orders.
        # It just returns a successful response for all items in the request.
        created = []
        errors = []
        for item in request.items or []:
            created.append(
                click_and_drop_api.UpdatedOrderInfo(
                    order_identifier=item.order_identifier,
                    order_reference=item.order_reference,
                    status=item.status,
                )
            )

        return click_and_drop_api.UpdateOrderStatusResponse(
            updated_orders=created,
            errors=errors,
        )


__all__ = ["MockClickAndDrop"]
