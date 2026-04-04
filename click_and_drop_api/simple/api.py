"""The simple API interface."""

from dataclasses import dataclass
from typing import Literal, Optional, Union
from .base import AbstractClickAndDrop
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


@dataclass
class AccountCacheEntry:
    """A cache entry per API key."""

    api_key: str
    is_oba: Optional[bool] = None


ACCOUNT_CACHE: dict[str, AccountCacheEntry] = {}


class ClickAndDrop(AbstractClickAndDrop):
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
    def _account_cache(self) -> AccountCacheEntry:
        """Cached account information for speed."""
        result = ACCOUNT_CACHE.get(self._key)
        if result is None:
            result = AccountCacheEntry(self._key)
            ACCOUNT_CACHE[self._key] = result
        return result

    def is_oba(self) -> bool:
        """Wether this is an OBA account.

        Check wether this is an OBA account by trying to create an order service code.
        """
        if self._account_cache.is_oba is not None:
            return self._account_cache.is_oba
        result = super().is_oba()
        self._account_cache.is_oba = result
        return result

    @property
    def key(self) -> str:
        """The API key in use."""
        return self._key

    def _get_orders(
        self, order_identifiers: Union[list[Union[str, int]]]
    ) -> list[click_and_drop_api.GetOrderInfoResource]:
        return self._orders_api.get_specific_orders_async(
            order_identifiers=order_identifiers_to_string(order_identifiers)
        )

    def _delete_orders(
        self, order_identifiers: list[Union[str, int]]
    ) -> click_and_drop_api.DeleteOrdersResource:
        return self._orders_api.delete_orders_async(
            order_identifiers=order_identifiers_to_string(order_identifiers)
        )

    def _create_orders(
        self, orders: Union[list[CreateOrder], CreateOrder]
    ) -> click_and_drop_api.CreateOrdersResponse:
        if not isinstance(orders, list):
            orders = [orders]
        request = click_and_drop_api.CreateOrdersRequest(items=orders)
        return self._orders_api.create_orders_async(request)

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

    def _set_order_status(
        self, request: click_and_drop_api.UpdateOrdersStatusRequest
    ) -> click_and_drop_api.UpdateOrderStatusResponse:
        return self._orders_api.update_orders_status_async(request)

    def _manifest_orders(
        self, request: click_and_drop_api.ManifestEligibleOrdersRequest
    ) -> click_and_drop_api.ManifestOrdersResponse:
        return self._manifests_api.manifest_eligible_async(request)


__all__ = ["ClickAndDrop"]
