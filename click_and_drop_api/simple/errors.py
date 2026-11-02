"""Errors raised by the simple API.

All of them are subclasses of :class:`ClickAndDropError`.
Errors of the HTTP layer are raised as
:class:`click_and_drop_api.exceptions.ApiException` instead.
Orders that cannot be created are not errors: they are returned in
``failed_orders`` of the result, see :mod:`click_and_drop_api.simple.strategy`.
"""

from __future__ import annotations


class ClickAndDropError(Exception):
    """Base class of all errors raised by the simple API."""


class InvalidWeight(ClickAndDropError, ValueError):
    """The weight cannot be shipped by this package size."""


class InvalidDimensions(ClickAndDropError, ValueError):
    """The dimensions cannot be shipped by this package size."""


__all__ = [
    "ClickAndDropError",
    "InvalidWeight",
    "InvalidDimensions",
]
