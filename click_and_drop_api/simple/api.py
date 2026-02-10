"""The simple API interface."""

from typing import Optional, Union
from .types import CreateOrder
import click_and_drop_api

from urllib.parse import quote


def id_or_ref_to_string(id_or_ref: Union[int, str]) -> str:
    """Encode order ids and strings."""
    if isinstance(id_or_ref, int):
        return str(id_or_ref)
    elif isinstance(id_or_ref, str):
        return f'"{quote(id_or_ref)}"'
    raise TypeError(f"Expected int or str, got {id_or_ref}.")


class ClickAndDrop:
    """The Click & Drop API simplified."""

    host = "https://api.parcel.royalmail.com/api/v1"
    """The Click & Drop API host.
    
    There seems to be only one host available.
    """

    def __init__(self, key: str):
        """Create a new API object.

        Parameters:
            key: The Click & Drop API authorisation key.
        """
        if not isinstance(key, str):
            raise TypeError(f"Expected str, got {key}.")
        key = key.strip()
        if not 30 < len(key) < 40:
            raise ValueError(f"Expected 36 characters, got {len(key)}.")
        if "".join(key.split()) != key:
            raise ValueError(f"Expected no whitespace in {key!r}.")
        self._key = key
        self._configuration = click_and_drop_api.Configuration(host=self.host)
        self._configuration.api_key["Bearer"] = self._key
        self._api_client = click_and_drop_api.ApiClient(self._configuration)
        self._version_api = click_and_drop_api.VersionApi(self._api_client)
        self._orders_api = click_and_drop_api.OrdersApi(self._api_client)
        self._labels_api = click_and_drop_api.LabelsApi(self._api_client)
        self._manifests_api = click_and_drop_api.ManifestsApi(self._api_client)

    def get_version(self) -> click_and_drop_api.GetVersionResource:
        """Get the version of the Click & Drop API.

        https://api.parcel.royalmail.com/#tag/Version
        """
        return self._version_api.get_version_async()

    @property
    def key(self) -> str:
        """The API key in use."""
        return self._key

    def get_orders(
        self, order_identifiers: Union[list[Union[str, int]], str, int]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        """Get specific orders.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.
                The maximum number of identifiers is 100.

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetSpecificOrdersAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        return self._orders_api.get_specific_orders_async(
            order_identifiers=";".join(map(id_or_ref_to_string, order_identifiers))
        )

    def get_order(
        self, order_identifier: Union[str, int]
    ) -> Optional[click_and_drop_api.GetOrderInfoResource]:
        """Get a specific order.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.
                The maximum number of identifiers is 100.

        Returns:
            The order or None if not found.

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetOrderAsync
        """
        orders = self.get_orders(order_identifier)
        return orders[0] if orders else None

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
                The maximum number of identifiers is 100.

        https://api.parcel.royalmail.com/#tag/Orders/operation/DeleteOrdersAsync
        """
        if not isinstance(order_identifiers, list):
            order_identifiers = [order_identifiers]
        return self._orders_api.delete_orders_async(
            order_identifiers=";".join(map(id_or_ref_to_string, order_identifiers))
        )

    def create_orders(
        self, orders: Union[list[CreateOrder], CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a new order.

        https://api.parcel.royalmail.com/#tag/Orders/operation/CreateOrdersAsync
        """
        if not isinstance(orders, list):
            orders = [orders]
        request = click_and_drop_api.CreateOrdersRequest(items=orders)
        return self._orders_api.create_orders_async(request)

    def create_order(
        self, order: CreateOrder
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a new order.

        https://api.parcel.royalmail.com/#tag/Orders/operation/CreateOrdersAsync
        """
        return self.create_orders(order)
