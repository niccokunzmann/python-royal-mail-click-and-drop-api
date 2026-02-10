"""Renamed types for nicer reading"""

from click_and_drop_api import CreateOrderRequest as CreateOrder
from click_and_drop_api import RecipientDetailsRequest as RecipientDetails
from click_and_drop_api import AddressRequest as Address

__all__ = ["CreateOrder", "RecipientDetails", "Address"]
