"""In-memory mock of the ClickAndDrop API for use in tests."""

from __future__ import annotations

import base64
from collections import Counter
from importlib.resources import files
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Union

import click_and_drop_api

from .base import AbstractClickAndDrop
from .strategy import CreateOrderStrategy, NullStrategy
from .shipping.db import ShippingDB
from .types import CreateOrder
from click_and_drop_api.exceptions import BadRequestException, ForbiddenException
from click_and_drop_api.models.error_response import ErrorResponse

_MOCK_KEY = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
_MOCK_VERSION = "1.0.0-mock"

EU_COUNTRY_CODES = frozenset(
    "AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE".split()
)
"""ISO 3166-1 alpha-2 codes of the EU member states."""

# Items declared as these categories need a manufacturer ID for EU shipments.
# Royal Mail also rejects items without a category.
_SALE_OF_GOODS_CATEGORIES = (None, "commercialSaleOfGoods", "eCommerceSaleOfGoods")


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
        create_order_strategy: Optional[CreateOrderStrategy] = None,
        channel_shipper: bool = True,
    ):
        """Create a new API object.

        Parameters:
            key: The Click & Drop API authorisation key.
            is_oba: Whether to treat the API as OBA.
            despatch_when_manifested: Whether to despatch orders when they are manifested.
            create_order_strategy: The strategy to check orders before they are created.
            channel_shipper: Whether the account is a ChannelShipper account.
                Only these can get order details, others get 403.

        Raises:
            TypeError: The key is not a string.
            ValueError: The key does not have about 36 characters or contains whitespace.
        """
        if not isinstance(key, str):
            raise TypeError(f"Expected str, got {key}.")
        key = key.strip()
        if not 30 < len(key) < 40:
            raise ValueError(f"Expected 36 characters, got {len(key)}.")
        if "".join(key.split()) != key:
            raise ValueError(f"Expected no whitespace in {key!r}.")
        self._key = key
        self.create_order_strategy = (
            NullStrategy() if create_order_strategy is None else create_order_strategy
        )
        self._is_oba = is_oba
        self._channel_shipper = channel_shipper
        self._orders: dict[int, click_and_drop_api.GetOrderInfoResource] = {}
        self._order_statuses: dict[int, Optional[str]] = {}
        self._next_id = 1
        self.page_requests: list[tuple] = []
        """The (start, end, continuation_token) of each requested page, for tests."""
        self._next_manifest_id = 1
        self.despatch_when_manifested = despatch_when_manifested
        self.__now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        """The current time of the mock."""
        return self.__now

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
        failed = []
        counts = Counter(order.order_reference for order in orders)
        for order in orders:
            errors = self._validate_order(order)
            if counts[order.order_reference] > 1:
                # Click & Drop rejects all orders with this reference.
                errors = [
                    click_and_drop_api.CreateOrderErrorResponse(
                        error_code=76,
                        error_message="Property 'OrderReference' must be unique among provided items",
                        fields=[
                            click_and_drop_api.OrderFieldResponse(
                                field_name="OrderReference", value=order.order_reference
                            )
                        ],
                    )
                ]
            if errors:
                failed.append(
                    click_and_drop_api.FailedOrderResponse(order=order, errors=errors)
                )
                continue
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
            errors_count=len(failed),
            created_orders=created,
            failed_orders=failed,
        )

    def _validate_order(
        self, order: CreateOrder
    ) -> list[click_and_drop_api.CreateOrderErrorResponse]:
        """Return the errors Royal Mail would report for this order."""
        errors = []
        service_code = (
            order.postage_details.service_code if order.postage_details else None
        )
        # Tested with a non-OBA account: it rejects unknown and OBA service codes.
        # Not tested with an OBA account, so it accepts all known service codes.
        codes = (
            ShippingDB.default() if self._is_oba else self.shipping_options
        ).service_codes()
        if service_code and service_code not in codes:
            errors.append(
                click_and_drop_api.CreateOrderErrorResponse(
                    error_code=31,
                    error_message=f"Service code '{service_code}' could not be found or it's not supported by Royal Mail.",
                    fields=[
                        click_and_drop_api.OrderFieldResponse(
                            field_name="PostageDetails.ServiceCode", value=service_code
                        )
                    ],
                )
            )
        if order.recipient.address.country_code in EU_COUNTRY_CODES:
            for package in order.packages or []:
                for item in package.contents or []:
                    if (
                        item.customs_declaration_category in _SALE_OF_GOODS_CATEGORIES
                        and not item.non_standardised_manufacturer_id
                        and not item.standardised_manufacturer_id
                    ):
                        errors.append(
                            click_and_drop_api.CreateOrderErrorResponse(
                                error_code=119,
                                error_message=(
                                    "Mandatory fields are missing from an order that is"
                                    " being sent to the EU or USA. Please ensure all"
                                    " fields are provided and re-submit order."
                                ),
                                fields=[
                                    click_and_drop_api.OrderFieldResponse(
                                        field_name="Packages.Contents.NonStandardisedManufacturerId",
                                        value=None,
                                    )
                                ],
                            )
                        )
        return errors

    def _get_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = []
        ambiguous = []
        missing_ids = []
        missing_refs = []
        for identifier in order_identifiers:
            if isinstance(identifier, int):
                order = self._orders.get(identifier)
                if order is None:
                    missing_ids.append(identifier)
                else:
                    result.append(order)
            elif isinstance(identifier, str):
                orders = self._orders_with_reference(identifier)
                if len(orders) > 1:
                    ambiguous.append(identifier)
                elif not orders:
                    missing_refs.append(identifier)
                else:
                    result.extend(orders)
        # Click & Drop answers with 400 if no order is found.
        # Missing and ambiguous references next to found orders are left out.
        if not result and (missing_ids or missing_refs or ambiguous):
            errors = [
                click_and_drop_api.OrderErrorResponse(
                    account_order_number=identifier, code="2", message=self._MISSING_ID
                )
                for identifier in missing_ids
            ]
            errors.extend(
                self._order_error(reference, "3", self._MISSING)
                if reference in missing_refs
                else self._order_error(
                    reference, self.AMBIGUOUS_REFERENCE, self._AMBIGUOUS
                )
                for reference in order_identifiers
                if reference in missing_refs or reference in ambiguous
            )
            errors.append(
                self._order_error(
                    self._identifier_list(order_identifiers), "1", self._INVALID
                )
            )
            raise BadRequestException(
                status=400,
                reason="Bad Request",
                body="[" + ",".join(e.to_json() for e in errors) + "]",
                data=errors,
            )
        return result

    _AMBIGUOUS = (
        "Ambiguous reference: Provided reference has multiple orders associated with it"
    )
    _MISSING = "Order with provided reference does not exist. Please verify that all references provided are URL encoded"
    _INVALID = "Some or all of provided ids and references are invalid. Please verify that all provided references are URL encoded"
    _MISSING_ID = "Order with provided id does not exist"

    @staticmethod
    def _identifier_list(order_identifiers) -> str:
        """The identifiers as Click & Drop repeats them in error code 1."""
        return ";".join(
            f'"{i}"' if isinstance(i, str) else str(i) for i in order_identifiers
        )

    @staticmethod
    def _order_error(reference: str, code: str, message: str):
        return click_and_drop_api.OrderErrorResponse(
            channel_order_reference=reference, code=code, message=message
        )

    def _orders_with_reference(
        self, reference: str
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        return [o for o in self._orders.values() if o.order_reference == reference]

    def _get_orders_page(
        self,
        page_size: int,
        start: Optional[datetime],
        end: Optional[datetime],
        continuation_token: Optional[str],
    ) -> click_and_drop_api.GetOrdersResponse:
        self.page_requests.append((start, end, continuation_token))
        # Click & Drop cuts the times off to whole seconds.
        start = start.replace(microsecond=0) if start is not None else None
        end = end.replace(microsecond=0) if end is not None else None
        if start is not None and end is not None and end <= start:
            raise BadRequestException(
                status=400,
                reason="Bad Request",
                body='{"code":"REQUEST_VALIDATION_FAILED","message":"\'endDateTime\' should be greater than \'startDateTime\'","details":""}',
            )
        # The token is the last identifier of the previous page,
        # so that deleting orders does not skip any.
        before = int(continuation_token) if continuation_token else None
        orders = sorted(
            (
                order
                for order in self._orders.values()
                if (start is None or order.created_on >= start)
                and (end is None or order.created_on < end)
                and (before is None or order.order_identifier < before)
            ),
            key=lambda o: o.order_identifier,
            reverse=True,
        )
        page = orders[:page_size]
        more = len(orders) > page_size
        return click_and_drop_api.GetOrdersResponse(
            orders=page,
            continuation_token=str(page[-1].order_identifier) if more else None,
        )

    def _get_orders_details(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderDetailsResource]:
        if not self._channel_shipper:
            raise ForbiddenException(
                status=403,
                reason="Forbidden",
                body='{"message":"Forbidden (Feature not available)"}',
            )
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
        ambiguous = [
            reference
            for reference in order_identifiers
            if isinstance(reference, str)
            and len(self._orders_with_reference(reference)) > 1
        ]
        if ambiguous:
            # Click & Drop deletes nothing and lists the copies that could be deleted.
            errors = []
            for reference in ambiguous:
                errors.append(
                    click_and_drop_api.OrderErrorInfo(
                        order_reference=reference,
                        code="22",
                        message="Ambiguous reference: Provided reference has multiple orders associated with it, several of which are eligible",
                    )
                )
                errors.extend(
                    click_and_drop_api.OrderErrorInfo(
                        order_identifier=order.order_identifier,
                        order_reference=reference,
                        code="23",
                        message="Order is eligible for deletion, but is not unique for provided reference",
                    )
                    for order in self._orders_with_reference(reference)
                    if order.manifested_on is None
                )
            raise BadRequestException(
                status=400,
                reason="Bad Request",
                body="[" + ",".join(e.to_json() for e in errors) + "]",
                data=errors,
            )
        deleted = []
        missing_ids = []
        missing_refs = []
        manifested = []
        for identifier in order_identifiers:
            if isinstance(identifier, int):
                order = self._orders.get(identifier)
            else:
                orders = self._orders_with_reference(identifier)
                order = orders[0] if orders else None
            if order is None:
                (missing_ids if isinstance(identifier, int) else missing_refs).append(
                    identifier
                )
            elif order.manifested_on is not None:
                manifested.append(order)
            else:
                del self._orders[order.order_identifier]
                self._order_statuses.pop(order.order_identifier, None)
                deleted.append(
                    click_and_drop_api.DeletedOrderInfo(
                        order_identifier=order.order_identifier,
                        order_reference=order.order_reference,
                    )
                )
        errors = [
            click_and_drop_api.OrderErrorInfo(
                order_identifier=identifier, code="2", message=self._MISSING_ID
            )
            for identifier in missing_ids
        ] + [
            click_and_drop_api.OrderErrorInfo(
                order_reference=reference, code="3", message=self._MISSING
            )
            for reference in missing_refs
        ]
        if errors:
            errors.append(
                click_and_drop_api.OrderErrorInfo(
                    order_reference=self._identifier_list(order_identifiers),
                    code="1",
                    message=self._INVALID,
                )
            )
        # Not tested against Click & Drop: deleting a manifested order needs postage.
        errors.extend(
            click_and_drop_api.OrderErrorInfo(
                order_identifier=order.order_identifier,
                order_reference=order.order_reference,
                code="MANIFESTED",
                message="Manifested orders cannot be deleted.",
            )
            for order in manifested
        )
        if errors and not deleted:
            # Click & Drop answers with 400 if no order is deleted.
            raise BadRequestException(
                status=400,
                reason="Bad Request",
                body="[" + ",".join(e.to_json() for e in errors) + "]",
                data=errors,
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
        """Create the API with the key from an environment variable.

        Raises:
            click_and_drop_api.exceptions.ForbiddenException: The account is not an OBA account.
        """
        if not self._is_oba:
            raise ForbiddenException(
                status=403,
                reason="Forbidden",
                body='{"message":"Forbidden (Feature not available)"}',
            )
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
