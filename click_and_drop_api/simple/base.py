"""Abstract base class for the Click & Drop API."""

from __future__ import annotations

from abc import ABC, abstractmethod
import os
from typing import Iterator, Literal, Optional, Union
from click_and_drop_api.simple.compatibility import Self

import click_and_drop_api

import uuid
from datetime import datetime, timedelta, timezone

from click_and_drop_api.exceptions import ApiException, BadRequestException
from click_and_drop_api.models.create_order_response import CreateOrderResponse
from click_and_drop_api.models.manifest_eligible_orders_request import (
    ManifestEligibleOrdersRequest,
)
from click_and_drop_api.models.manifest_orders_response import ManifestOrdersResponse
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
from click_and_drop_api.simple.shipping.db import ShippingDB
from click_and_drop_api.simple.shipping_test_result import ShippingTestResult
from click_and_drop_api.simple.addresses import get_address, get_all_country_codes
from .types import ManifestedOrders, OrderInfo, ReferenceLookup, UpdateOrderStatus
from .strategy import CreateOrderStrategy, NullStrategy, delete_copies, failed_order


class AbstractClickAndDrop(ABC):
    """Common interface shared by ClickAndDrop and MockClickAndDrop.

    Every method that sends a request to Click & Drop can raise
    :class:`click_and_drop_api.exceptions.ApiException` or one of its subclasses:

    - :class:`~click_and_drop_api.exceptions.UnauthorizedException`: The API key is invalid (401).
    - :class:`~click_and_drop_api.exceptions.ApiException` with ``status`` 429:
      More than 5 requests per second.
    - :class:`~click_and_drop_api.exceptions.ServiceException`: Click & Drop has a problem (5xx).

    The ``Raises`` sections of the methods list the other errors and why they are raised.
    Orders that Click & Drop rejects one by one are not raised:
    they are in the ``failed_orders`` or ``errors`` of the results.
    """

    @classmethod
    def from_env(cls, api_env_var: str = "API_KEY") -> Self:
        """Create the API with the key from an environment variable.

        Raises:
            KeyError: The environment variable is not set.
            TypeError: The key is not a string.
            ValueError: The key does not have about 36 characters or contains whitespace.
        """
        api_key = os.environ[api_env_var]
        return cls(api_key)

    max_order_count: int = 100

    create_order_strategy: CreateOrderStrategy = NullStrategy()
    """The strategy that checks the orders before :meth:`create_orders` uploads them."""

    AMBIGUOUS_REFERENCE = "5"
    """Error code of Click & Drop: the reference has several orders."""

    @property
    def shipping_options(self) -> ShippingDB:
        """Return all the shipping options that can be used.

        Raises:
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        return ShippingDB.default().for_oba(self.is_oba())

    @property
    @abstractmethod
    def key(self) -> str:
        """The API key in use."""

    @abstractmethod
    def get_version(self) -> click_and_drop_api.GetVersionResource:
        """Get the API version.

        Raises:
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """

    @abstractmethod
    def _create_orders(
        self, orders: list[CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create one or more orders."""

    def create_orders(
        self,
        orders: Union[list[CreateOrder], CreateOrder],
        strategy: Optional[CreateOrderStrategy] = None,
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a new orders.

        Parameters:
            orders: One or more :class:`~click_and_drop_api.simple.types.CreateOrder` instances.
            strategy: The strategy to check the orders before the upload.
                Defaults to :attr:`create_order_strategy`.
        Returns:
            A :class:`~click_and_drop_api.models.create_orders_response.CreateOrdersResponse` instance containing created and failed orders.

            Orders rejected by the strategy are in ``failed_orders``,
            see :class:`~click_and_drop_api.simple.strategy.StrategyErrorCode`.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The request is invalid as a whole,
                e.g. more than one order asks for a label in the response.
                Orders that Click & Drop rejects one by one are not raised:
                they are in ``failed_orders`` of the result.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.

        https://api.parcel.royalmail.com/#tag/Orders/operation/CreateOrdersAsync
        """
        if isinstance(orders, CreateOrder):
            orders = [orders]
        prepared = (strategy or self.create_order_strategy).prepare(self, orders)
        orders = prepared.upload
        result = click_and_drop_api.CreateOrdersResponse(
            created_orders=[],
            failed_orders=list(prepared.failed),
            success_count=0,
            errors_count=len(prepared.failed),
        )
        for i in range(0, len(orders), self.max_order_count):
            response = self._create_orders(orders[i : i + self.max_order_count])
            result.created_orders.extend(response.created_orders)
            result.failed_orders.extend(response.failed_orders)
            result.success_count += response.success_count
            result.errors_count += response.errors_count
        return result

    def replace_orders(
        self,
        orders: Union[list[CreateOrder], CreateOrder],
        delete_printed: bool = False,
        lookback: Optional[timedelta] = None,
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create orders and delete the other orders with the same references.

        This assumes that the references do not exist yet:
        the orders are uploaded in as few requests as possible
        and then the references are looked up in one request.
        Only if a reference now has several orders, the older ones are deleted.

        If an older order cannot be deleted, the new order is deleted instead,
        so that the reference is not duplicated.  It is in ``failed_orders``
        with a :class:`~click_and_drop_api.simple.strategy.StrategyErrorCode`:

        - ``ORDER_MANIFESTED``: Manifested orders cannot be deleted.
        - ``LABEL_ALREADY_PRINTED``: The label is printed and ``delete_printed`` is false.
        - ``DELETE_FAILED``: Click & Drop did not delete it.

        Parameters:
            orders: The orders to create.
            delete_printed: Also delete older orders with a printed label.
                This cancels the label.  Royal Mail charges for parcels sent
                with a cancelled label.
            lookback: Only search the orders uploaded in this time for older orders.
                ``None`` searches all orders.

        Returns:
            The created and the failed orders, like :meth:`create_orders`.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The request is invalid as a whole,
                e.g. more than one order asks for a label in the response.
                Orders that Click & Drop rejects one by one are not raised:
                they are in ``failed_orders`` of the result.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        if isinstance(orders, CreateOrder):
            orders = [orders]
        response = self.create_orders(orders, strategy=NullStrategy())
        new = {o.order_reference: o.order_identifier for o in response.created_orders}
        ambiguous = self.lookup_references(list(new)).ambiguous
        if not ambiguous:
            return response
        since = None if lookback is None else self.now() - lookback
        rejected = delete_copies(
            self,
            sorted(ambiguous),
            self.iter_recent_orders(until=since),
            delete_printed=delete_printed,
            keep=set(new.values()),
        )
        if rejected:
            self.delete_orders([new[reference] for reference in rejected])
            requests = {order.order_reference: order for order in orders}
            response.created_orders = [
                o for o in response.created_orders if o.order_reference not in rejected
            ]
            response.failed_orders.extend(
                failed_order(requests[reference], code, message)
                for reference, (code, message) in rejected.items()
            )
            response.success_count -= len(rejected)
            response.errors_count += len(rejected)
        return response

    def create_order(
        self, order: CreateOrder
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a single order.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The request is invalid as a whole,
                e.g. more than one order asks for a label in the response.
                Orders that Click & Drop rejects one by one are not raised:
                they are in ``failed_orders`` of the result.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        return self.create_orders(order)

    @abstractmethod
    def _get_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        """Retrieve orders by identifier or reference."""

    def get_orders(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> list[OrderInfo]:
        """Get specific orders.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.

        Returns:
            A list of :class:`~click_and_drop_api.simple.types.OrderInfo` instances.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: No order is found:
                an identifier (code ``"2"``) or reference (code ``"3"``) does not exist,
                or a reference has several orders (code ``"5"``).
                Missing and ambiguous orders next to found ones are left out without an error.
                Use :meth:`lookup_references` and :meth:`find_orders_by_reference` instead.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetSpecificOrdersAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = []
        for i in range(0, len(order_identifiers), self.max_order_count):
            result.extend(
                OrderInfo.from_get_order_info_resource(o)
                for o in self._get_orders(
                    order_identifiers[i : i + self.max_order_count]
                )
            )
        return result

    def lookup_references(self, references: list[str]) -> ReferenceLookup:
        """Look up orders by reference without listing the orders.

        Parameters:
            references: The order references to look for. May be empty.

        Returns:
            Which references are absent, unique or ambiguous,
            and the orders of the unique references.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: Click & Drop rejects the request
                for another reason than missing or ambiguous references.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        lookup = ReferenceLookup()
        references = list(dict.fromkeys(references))
        for i in range(0, len(references), self.max_order_count):
            self._lookup_batch(references[i : i + self.max_order_count], lookup)
        return lookup

    def _lookup_batch(self, references: list[str], lookup: ReferenceLookup) -> None:
        """Look up references with one request each round.

        Click & Drop leaves out missing and ambiguous references next to
        unique ones without an error.  These are looked up again without the
        unique ones: then Click & Drop reports each of them with an error.
        """
        unknown = references
        while unknown:
            try:
                infos = self.get_orders(unknown)
            except BadRequestException as error:
                if not isinstance(error.data, list):
                    raise
                codes = {
                    e.channel_order_reference: e.code
                    for e in error.data
                    if e.code in (self.AMBIGUOUS_REFERENCE, *self.NOT_FOUND)
                }
                for reference in unknown:
                    if codes.get(reference) == self.AMBIGUOUS_REFERENCE:
                        lookup.ambiguous.add(reference)
                    elif reference in codes:
                        lookup.absent.add(reference)
                still_unknown = [r for r in unknown if r not in codes]
                if len(still_unknown) == len(unknown):
                    raise
                unknown = still_unknown
                continue
            for info in infos:
                lookup.orders[info.order_reference] = info
                lookup.unique.add(info.order_reference)
            still_unknown = [r for r in unknown if r not in lookup.orders]
            if len(still_unknown) == len(unknown):
                lookup.absent.update(unknown)  # no error, no order
                return
            unknown = still_unknown

    def find_orders_by_reference(
        self,
        references: list[str],
        since: Optional[datetime] = None,
        orders: Optional[Iterator[OrderInfo]] = None,
    ) -> dict[str, list[OrderInfo]]:
        """Find the orders on Click & Drop for each reference.

        A reference with one order is looked up directly.
        Click & Drop accepts several orders with the same reference
        but cannot look them up by that reference.
        These orders are found with :meth:`iter_orders` instead.
        Click & Drop does not tell how many orders a reference has,
        so the search stops as soon as two orders are found for each of these
        references.  There may be more: delete the found orders and search again
        with the same ``orders`` so that no orders are listed twice.

        The orders are searched from the newest to the oldest,
        see :meth:`iter_recent_orders`, so recent duplicates are found fast.

        Parameters:
            references: The order references to look for. May be empty.
            since: Only search orders created after this time for references
                that have several orders.
            orders: Continue searching in these orders, e.g. the iterator of a
                previous search, instead of starting a new :meth:`iter_recent_orders`.

        Returns:
            A dictionary mapping each reference to its orders.
            The list is empty if the reference does not exist.
            It has two or more orders if the reference has several orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: Click & Drop rejects the request
                for another reason than missing or ambiguous references.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        result: dict[str, list[OrderInfo]] = {reference: [] for reference in references}
        lookup = self.lookup_references(references)
        for reference, info in lookup.orders.items():
            result[reference].append(info)
        ambiguous = lookup.ambiguous
        if ambiguous:
            if orders is None:
                orders = self.iter_recent_orders(until=since)
            # How many more orders to find for each reference.
            missing = {reference: 2 for reference in ambiguous}
            for info in orders:
                if info.order_reference in ambiguous:
                    result[info.order_reference].append(info)
                    if missing.get(info.order_reference) == 1:
                        del missing[info.order_reference]
                        if not missing:
                            break
                    elif info.order_reference in missing:
                        missing[info.order_reference] -= 1
        return result

    def now(self) -> datetime:
        """The current time of Click & Drop."""
        return datetime.now(timezone.utc)

    @abstractmethod
    def _get_orders_page(
        self,
        page_size: int,
        start: Optional[datetime],
        end: Optional[datetime],
        continuation_token: Optional[str],
    ) -> click_and_drop_api.GetOrdersResponse:
        """Retrieve one page of orders."""

    def iter_orders(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Iterator[OrderInfo]:
        """Iterate over all orders, page by page, from the newest to the oldest.

        Click & Drop filters by the time the order was uploaded (``created_on``),
        not by ``order_date``.
        It cuts the times off to whole seconds:
        ``start`` is inclusive, ``end`` is exclusive.
        Each page is requested once.  The next page continues after the last
        order of the previous one, so deleting orders while iterating skips none.

        Parameters:
            start: Only orders uploaded at or after this time.
            end: Only orders uploaded before this time.
                It must be at least one second after ``start``.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: ``end`` is not at least
                one second after ``start``: "'endDateTime' should be greater than 'startDateTime'".
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetOrdersAsync
        """
        token = None
        while True:
            page = self._get_orders_page(self.max_order_count, start, end, token)
            for order in page.orders or []:
                yield OrderInfo.from_get_order_info_resource(order)
            token = page.continuation_token
            if not token:
                return

    def iter_recent_orders(
        self, until: Optional[datetime] = None
    ) -> Iterator[OrderInfo]:
        """Iterate over the orders from the newest to the oldest.

        Click & Drop lists the newest orders first, so stopping early saves requests.

        Parameters:
            until: Stop at orders uploaded before this time.
                ``None`` iterates over all orders.

        Raises:
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        return self.iter_orders(start=until)

    def get_order(self, order_identifier: Union[str, int]) -> Optional[OrderInfo]:
        """Retrieve a single order.

        Parameters:
            order_identifier: Order Identifier (integer) or Order Reference (string).

        Returns:
            The order if found, else None.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The reference has
                several orders (error code ``"5"``).
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        try:
            orders = self.get_orders(order_identifier)
        except BadRequestException as error:
            if self._is_not_found(error):
                return None
            raise
        return orders[0] if orders else None

    NOT_FOUND = {"1", "2", "3"}
    """Error codes of Click & Drop: the order does not exist."""

    def _is_not_found(self, error: BadRequestException) -> bool:
        """Whether Click & Drop only reports that orders do not exist."""
        return isinstance(error.data, list) and all(
            getattr(e, "code", None) in self.NOT_FOUND for e in error.data
        )

    @abstractmethod
    def _get_orders_details(
        self, order_identifiers: list[Union[str, int]]
    ) -> list[click_and_drop_api.GetOrderDetailsResource]:
        """Retrieve detailed order information by identifier or reference."""

    def get_orders_details(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> list[click_and_drop_api.GetOrderDetailsResource]:
        """Get detailed information for specific orders, including order status.

        .. note::
            Reserved for ChannelShipper customers only.
            Please visit https://channelshipper.com/ for more information.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.

        Returns:
            A list of :class:`~click_and_drop_api.models.get_order_details_resource.GetOrderDetailsResource`
            instances, each including ``order_status`` and timestamps such as
            ``postage_applied_on`` and ``manifested_on``.

        Raises:
            click_and_drop_api.exceptions.ForbiddenException: If the account is not a
                ChannelShipper account (HTTP 403).
            click_and_drop_api.exceptions.BadRequestException: No order is found,
                see :meth:`get_orders`.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetSpecificOrdersWithDetailsAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = []
        for i in range(0, len(order_identifiers), self.max_order_count):
            result.extend(
                self._get_orders_details(
                    order_identifiers[i : i + self.max_order_count]
                )
            )
        return result

    def get_order_details(
        self, order_identifier: Union[str, int]
    ) -> Optional[click_and_drop_api.GetOrderDetailsResource]:
        """Get detailed information for a single order, including order status.

        .. note::
            Reserved for ChannelShipper customers only.
            Please visit https://channelshipper.com/ for more information.

        Parameters:
            order_identifier: Order Identifier (integer) or Order Reference (string).

        Returns:
            The order details if found, else None.

        Raises:
            click_and_drop_api.exceptions.ForbiddenException: If the account is not a
                ChannelShipper account (HTTP 403).
            click_and_drop_api.exceptions.BadRequestException: The reference has
                several orders (error code ``"5"``).
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        try:
            results = self.get_orders_details(order_identifier)
        except BadRequestException as error:
            if self._is_not_found(error):
                return None
            raise
        return results[0] if results else None

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

        Returns:
            The deleted orders and the errors.
            Click & Drop answers with 400 if no order of a request is deleted,
            e.g. because none exists.  These errors are in the result, too,
            so that the result does not depend on how the orders are split
            into requests.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The request is invalid
                in another way, e.g. a reference has several orders (codes ``"22"``, ``"23"``).
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.

        https://api.parcel.royalmail.com/#tag/Orders/operation/DeleteOrdersAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        result = click_and_drop_api.DeleteOrdersResource(deleted_orders=[], errors=[])
        for i in range(0, len(order_identifiers), self.max_order_count):
            try:
                deleted = self._delete_orders(
                    order_identifiers[i : i + self.max_order_count]
                )
            except BadRequestException as error:
                if not self._is_not_deletable(error):
                    raise
                result.errors.extend(error.data)
                continue
            result.deleted_orders.extend(deleted.deleted_orders)
            result.errors.extend(deleted.errors or [])
        return result

    def _is_not_deletable(self, error: BadRequestException) -> bool:
        """Whether Click & Drop only reports orders that cannot be deleted one by one."""
        return isinstance(error.data, list) and all(
            isinstance(e, click_and_drop_api.OrderErrorInfo)
            and e.code not in self.AMBIGUOUS_DELETE
            for e in error.data
        )

    AMBIGUOUS_DELETE = {"22", "23"}
    """Error codes of Click & Drop: a reference to delete has several orders."""

    def delete_order(
        self, order_identifier: Union[str, int]
    ) -> click_and_drop_api.DeleteOrdersResource:
        """Delete a single order.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The reference has several orders
                (codes ``"22"``, ``"23"``).  Orders that cannot be deleted one by one
                are in ``errors`` of the result.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        return self.delete_orders(order_identifier)

    @abstractmethod
    def get_label(
        self,
        order_identifiers: Union[list[Union[str, int]], str, int],
        document_type: Literal["postageLabel", "despatchNote", "CN22", "CN23"],
        include_returns_label: Optional[bool] = None,
        include_cn: Optional[bool] = None,
    ) -> bytearray:
        """Generate a label PDF for one or more orders.

        Raises:
            click_and_drop_api.exceptions.ForbiddenException: The account is not an OBA account.
            click_and_drop_api.exceptions.BadRequestException: An order does not exist
                or has no postage applied.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """

    NON_OBA_TEST_SERVICE_CODE = "OLP1"

    def is_oba(self) -> bool:
        """Wether this is an OBA account.

        Check wether this is an OBA account by trying to create an order service code.

        Raises:
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
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

        Raises:
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
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

        Raises:
            ValueError: No address is given.
            KeyError: A country code has no test address.
            click_and_drop_api.exceptions.ApiException: The test orders could not be deleted.
                Errors while creating them are in the result.
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
        else:
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

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
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
        """Update the status of multiple orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
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
        """Set the status of orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        return self.update_order_status(
            self._get_orders_update_request(order_identifiers, status=status)
        )

    def set_order_tracking_number(
        self, order_identifiers: list[Union[str, int]] | str | int, tracking_number: str
    ) -> UpdateOrderStatusResponse:
        """Set the tracking number of a orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
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
        """Set the despatch date of a orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
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
        """Set the shipping carrier of a orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
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
        """Set the shipping service of a orders.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The update is invalid,
                e.g. a tracking number without despatch date, carrier and service,
                or an order does not exist.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
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

    @abstractmethod
    def _manifest_orders(
        self, request: ManifestEligibleOrdersRequest
    ) -> ManifestOrdersResponse:
        """Manifest eligible orders."""

    CARRIER_NAME_OBA = "Royal Mail OBA"
    CARRIER_NAME_OLP = "Royal Mail OLP"

    def get_default_carrier_name(self) -> str:
        """Return the carrier name for this account.

        Returns ``"Royal Mail OBA"`` for OBA accounts and ``"Royal Mail OLP"``
        for standard accounts.  Override to use a custom carrier name.

        Raises:
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.
        """
        return self.CARRIER_NAME_OBA if self.is_oba() else self.CARRIER_NAME_OLP

    def manifest_orders(self, carrier_name: str | None = ...) -> ManifestedOrders:
        """Manifest all eligible orders, applying postage.

        Manifests all orders in ``Label Generated`` and ``Despatched`` statuses
        and returns manifest paperwork where possible.

        Parameters:
            carrier_name:
                The carrier name to manifest for.  Must match the name
                configured in **Settings → Carrier settings** on the Click &
                Drop website.  When omitted, :meth:`get_default_carrier_name` is called
                to select the name automatically (``"Royal Mail OBA"`` for OBA
                accounts, ``"Royal Mail OLP"`` for standard accounts).  Pass
                ``None`` explicitly for single-carrier accounts.

        Returns:
            A :class:`~click_and_drop_api.models.manifest_orders_response.ManifestOrdersResponse`
            containing the manifest number and an optional base64-encoded PDF.

        Raises:
            click_and_drop_api.exceptions.BadRequestException: The orders cannot be manifested,
                e.g. the carrier name is required because the account has several carriers.
            click_and_drop_api.exceptions.ApiException: The request failed, see :class:`AbstractClickAndDrop`.

        https://api.parcel.royalmail.com/#tag/Manifests/operation/ManifestEligibleAsync
        """
        if carrier_name is ...:
            carrier_name = self.get_default_carrier_name()
        response = self._manifest_orders(
            ManifestEligibleOrdersRequest(carrier_name=carrier_name)
        )
        return ManifestedOrders(
            manifest_number=response.manifest_number,
            document_pdf=response.document_pdf,
        )


__all__ = [
    "AbstractClickAndDrop",
]
