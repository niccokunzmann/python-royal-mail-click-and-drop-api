"""Simple API access based on the generated API interface."""

from urllib.parse import quote

import click_and_drop_api
from click_and_drop_api import CreateOrderRequest as CreateOrder
from click_and_drop_api import RecipientDetailsRequest as RecipientDetails
from click_and_drop_api import AddressRequest as Address


def id_or_ref_to_string(id_or_ref: int | str) -> str:
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

    def get_specific_orders(
        self, order_identifiers: list[str | int] | str | int
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

    def delete_specific_orders(
        self, order_identifiers: list[str | int] | str | int
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
        self, orders: list[CreateOrder] | CreateOrder
    ) -> click_and_drop_api.CreateOrdersResponse:
        """Create a new order.

        https://api.parcel.royalmail.com/#tag/Orders/operation/CreateOrdersAsync
        """
        if not isinstance(orders, list):
            orders = [orders]
        request = click_and_drop_api.CreateOrdersRequest(items=orders)
        return self._orders_api.create_orders_async(request)


__all__ = ["ClickAndDrop", "CreateOrder", "RecipientDetails", "Address"]
