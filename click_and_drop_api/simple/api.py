"""The simple API interface."""

from typing import Literal, Optional, Union
from .types import CreateOrder
import click_and_drop_api

from urllib.parse import quote


def order_identifier_to_string(id_or_ref: Union[int, str]) -> str:
    """Encode order ids and strings."""
    if isinstance(id_or_ref, int):
        return str(id_or_ref)
    elif isinstance(id_or_ref, str):
        return f'"{quote(id_or_ref)}"'
    raise TypeError(f"Expected int or str, got {id_or_ref}.")


def order_identifiers_to_string(
    order_identifiers: Union[list[Union[str, int]], str, int],
) -> str:
    """Encode order ids and references."""
    if not isinstance(order_identifiers, list):
        order_identifiers = [order_identifiers]
    return ";".join(map(order_identifier_to_string, order_identifiers))


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

        Returns:
            A list of orders

        Raises:
            click_and_drop_api.exceptions.BadRequestException if an order with the same reference already exists

        https://api.parcel.royalmail.com/#tag/Orders/operation/GetSpecificOrdersAsync
        """
        return self._orders_api.get_specific_orders_async(
            order_identifiers=order_identifiers_to_string(order_identifiers)
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

        Raises:
            click_and_drop_api.exceptions.BadRequestException if an order with the same reference already exists

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
        return self._orders_api.delete_orders_async(
            order_identifiers=order_identifiers_to_string(order_identifiers)
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

    def get_label(
        self,
        order_identifiers: Union[list[Union[str, int]], str, int],
        document_type: Literal["postageLabel", "despatchNote", "CN22", "CN23"],
        include_returns_label: Optional[bool] = None,
        include_cn: Optional[bool] = None,
    ) -> bytearray:
        r"""Generate a label for an order.

        Parameters:
            order_identifiers:
                One or several Order Identifiers or Order References.
                Order Identifiers are integer numbers.
                Order References are strings.
                The maximum number of identifiers is 100.
            document_type:
                Document generation mode.
                When documentType is set to "postageLabel" the additional parameters below must be used.
                These additional parameters will be ignored when documentType is not set to "postageLabel".
            include_returns_label:
                Include returns label.
                Required when documentType is set to 'postageLabel'.
            include_cn:
                Include CN22/CN23 with label.
                Optional parameter.
                If this parameter is used the setting will override the default account behaviour specified
                in the "Label format" setting "Generate customs declarations with orders".

        Returns:
            Return a single PDF file with generated label and/or associated document(s).

        ! Reserved for OBA customers only !
        The account "Label format" settings page will control the page format settings used to print the postage label and associated documents.
        Certain combinations of these settings may prevent associated documents from being printed together with the postage label within a single document.
        If this occurs the documentType option can be used in a separate call to print missing documents.

        Label generation only available for orders with postage applied status.

        https://api.parcel.royalmail.com/#tag/Labels/operation/GetOrdersLabelAsync
        """
        return self._labels_api.get_orders_label_async(
            order_identifiers=order_identifiers_to_string(order_identifiers),
            document_type=document_type,
            include_returns_label=include_returns_label,
            include_cn=include_cn,
        )


__all__ = ["ClickAndDrop"]
