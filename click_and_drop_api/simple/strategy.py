"""Strategies that check constraints before orders are created.

Pass a strategy to the API to choose what happens before an upload::

    api = ClickAndDrop(key, create_order_strategy=ReplaceDuplicateReferences())

The default is :class:`NullStrategy`, which uploads the orders as given.

Strategies do not raise errors for single orders.
Orders that violate a constraint are returned in ``failed_orders``
of the :class:`~click_and_drop_api.models.create_orders_response.CreateOrdersResponse`,
like orders that Click & Drop rejects.
Their error codes are the negative numbers of :class:`StrategyErrorCode`,
so that they differ from the error codes of Click & Drop.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from datetime import timedelta
from enum import IntEnum
from typing import TYPE_CHECKING, Collection, Iterator, Optional

import click_and_drop_api

if TYPE_CHECKING:
    from .base import AbstractClickAndDrop
    from .types import CreateOrder, OrderInfo


class StrategyErrorCode(IntEnum):
    """Error codes of orders rejected by a strategy."""

    DUPLICATE_REFERENCE = -1
    """An order with the same reference exists or is uploaded at the same time."""

    ORDER_MANIFESTED = -2
    """An existing order with the same reference is manifested and cannot be deleted."""

    LABEL_ALREADY_PRINTED = -3
    """An existing order with the same reference has a printed label.

    Deleting the order would cancel its label.
    Royal Mail charges for parcels sent with a cancelled label.
    """

    DELETE_FAILED = -4
    """Click & Drop did not delete an existing order with the same reference."""


@dataclass
class PreparedOrders:
    """The result of :meth:`CreateOrderStrategy.prepare`."""

    upload: list[CreateOrder]
    """The orders to upload."""

    failed: list[click_and_drop_api.FailedOrderResponse] = field(default_factory=list)
    """The orders that are not uploaded, with their errors."""

    def reject(
        self, references: set[str], code: StrategyErrorCode, message: str
    ) -> None:
        """Move the orders with these references from ``upload`` to ``failed``."""
        if not references:
            return
        rejected = [o for o in self.upload if o.order_reference in references]
        self.upload = [o for o in self.upload if o.order_reference not in references]
        self.failed.extend(failed_order(order, code, message) for order in rejected)


def failed_order(
    order: CreateOrder, code: StrategyErrorCode, message: str
) -> click_and_drop_api.FailedOrderResponse:
    """A failed order with an error of a strategy."""
    return click_and_drop_api.FailedOrderResponse(
        order=order,
        errors=[
            click_and_drop_api.CreateOrderErrorResponse(
                error_code=int(code),
                error_message=message,
                fields=[
                    click_and_drop_api.OrderFieldResponse(
                        field_name="orderReference", value=order.order_reference
                    )
                ],
            )
        ],
    )


class CreateOrderStrategy(ABC):
    """Decide what happens before orders are uploaded."""

    @abstractmethod
    def prepare(
        self, api: AbstractClickAndDrop, orders: list[CreateOrder]
    ) -> PreparedOrders:
        """Check the constraints.

        Returns:
            The orders to upload and the orders that failed.
        """


class NullStrategy(CreateOrderStrategy):
    """Upload the orders as given.

    Click & Drop accepts several orders with the same reference.
    """

    def prepare(
        self, api: AbstractClickAndDrop, orders: list[CreateOrder]
    ) -> PreparedOrders:
        return PreparedOrders(list(orders))


class _DuplicateReferenceStrategy(CreateOrderStrategy):
    """Reject orders with the same reference in one upload."""

    def prepare(
        self, api: AbstractClickAndDrop, orders: list[CreateOrder]
    ) -> PreparedOrders:
        prepared = PreparedOrders(list(orders))
        counts = Counter(order.order_reference for order in orders)
        prepared.reject(
            {reference for reference, count in counts.items() if count > 1},
            StrategyErrorCode.DUPLICATE_REFERENCE,
            "Several orders in this upload have the same reference.",
        )
        if prepared.upload:
            self.handle_existing(api, prepared)
        return prepared

    @staticmethod
    def references(prepared: PreparedOrders) -> list[str]:
        """The references of the orders to upload."""
        return [order.order_reference for order in prepared.upload]

    @abstractmethod
    def handle_existing(
        self, api: AbstractClickAndDrop, prepared: PreparedOrders
    ) -> None:
        """Handle the orders on Click & Drop with the same references."""


class RejectDuplicateReferences(_DuplicateReferenceStrategy):
    """Reject orders whose reference already exists on Click & Drop.

    Rejected orders are in ``failed_orders`` with the error code
    :attr:`StrategyErrorCode.DUPLICATE_REFERENCE`.
    The other orders are uploaded.
    This does not list all orders.
    """

    def handle_existing(self, api, prepared):
        prepared.reject(
            api.lookup_references(self.references(prepared)).existent,
            StrategyErrorCode.DUPLICATE_REFERENCE,
            "An order with this reference already exists.",
        )


class ReplaceDuplicateReferences(_DuplicateReferenceStrategy):
    """Replace existing orders with the same reference.

    Before the upload, all existing orders with the same reference are deleted,
    also duplicates that already exist.
    An order is not uploaded and is in ``failed_orders`` if its reference
    appears in another order of the upload, or an existing order with this
    reference cannot be deleted:

    - :attr:`StrategyErrorCode.ORDER_MANIFESTED`: Manifested orders cannot be deleted.
    - :attr:`StrategyErrorCode.LABEL_ALREADY_PRINTED`: The label is printed
      and ``delete_printed`` is false.
    - :attr:`StrategyErrorCode.DELETE_FAILED`: Click & Drop did not delete it.

    The other orders are uploaded.

    Click & Drop cannot look up a reference with several orders,
    so orders are listed until two of them are found.
    These are deleted and the reference is looked up again,
    until all of its orders are deleted.

    Parameters:
        lookback: Only list the orders uploaded in this time
            when searching for a reference with several orders.
            ``None`` searches all orders, so that all duplicates are removed.
        delete_printed: Also delete orders with a printed label.
            This cancels the label.  Royal Mail charges for parcels sent
            with a cancelled label, so only use this if printed labels
            are not used before the orders are manifested.
    """

    def __init__(
        self, lookback: Optional[timedelta] = None, delete_printed: bool = False
    ):
        self.lookback = lookback
        self.delete_printed = delete_printed

    def handle_existing(self, api, prepared):
        since = None if self.lookback is None else api.now() - self.lookback
        rejected = delete_copies(
            api,
            self.references(prepared),
            api.iter_recent_orders(until=since),
            delete_printed=self.delete_printed,
        )
        for reference, (code, message) in rejected.items():
            prepared.reject({reference}, code, message)


def delete_copies(
    api: AbstractClickAndDrop,
    references: list[str],
    orders: Iterator[OrderInfo],
    delete_printed: bool = False,
    keep: Collection[int] = (),
) -> dict[str, tuple[StrategyErrorCode, str]]:
    """Delete all orders with these references, except the ones to keep.

    Click & Drop cannot look up a reference with several orders,
    so ``orders`` are listed until two of them are found.
    These are deleted and the reference is looked up again,
    until all of its orders are deleted.
    The orders of a reference are only deleted if all of them can be deleted.

    Parameters:
        api: The API to use.
        references: The references whose orders to delete.
        orders: The orders to search, usually :meth:`~AbstractClickAndDrop.iter_recent_orders`.
            Continue the same iterator so that no orders are listed twice.
        delete_printed: Also delete orders with a printed label.
        keep: The identifiers of the orders not to delete.

    Returns:
        The references whose orders could not be deleted, with the reason.
    """
    rejected: dict[str, tuple[StrategyErrorCode, str]] = {}
    pending = list(references)
    while pending:
        existing = api.find_orders_by_reference(pending, orders=orders)
        copies = {
            reference: [info for info in infos if info.order_identifier not in keep]
            for reference, infos in existing.items()
        }
        for reference, infos in copies.items():
            if any(info.manifested_on is not None for info in infos):
                rejected[reference] = (
                    StrategyErrorCode.ORDER_MANIFESTED,
                    "An order with this reference is manifested and cannot be deleted.",
                )
            elif not delete_printed and any(
                info.printed_on is not None for info in infos
            ):
                rejected[reference] = (
                    StrategyErrorCode.LABEL_ALREADY_PRINTED,
                    "An order with this reference has a printed label."
                    " Deleting it would cancel the label.",
                )
        to_delete = {
            info.order_identifier: reference
            for reference, infos in copies.items()
            if reference not in rejected
            for info in infos
        }
        if not to_delete:
            break
        messages: dict[str, list[str]] = {}
        for error in api.delete_orders(list(to_delete)).errors:
            if error.code in api.NOT_FOUND:
                continue  # deleted at the same time, or code 1 repeating the request
            reference = to_delete.get(error.order_identifier, error.order_reference)
            messages.setdefault(reference, []).append(f"{error.code}: {error.message}")
        for reference, texts in messages.items():
            rejected[reference] = (
                StrategyErrorCode.DELETE_FAILED,
                "Could not delete the existing order with this reference: "
                + "; ".join(texts),
            )
        # References with several orders may have more of them.
        pending = [
            reference
            for reference in set(to_delete.values())
            if reference not in rejected and len(existing[reference]) >= 2
        ]
    return rejected


__all__ = [
    "CreateOrderStrategy",
    "NullStrategy",
    "PreparedOrders",
    "RejectDuplicateReferences",
    "ReplaceDuplicateReferences",
    "StrategyErrorCode",
    "delete_copies",
]
