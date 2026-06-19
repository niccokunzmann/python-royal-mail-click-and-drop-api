"""Tests for manifest_orders."""

import pytest

from click_and_drop_api.models.manifest_orders_response import ManifestOrdersResponse
from click_and_drop_api.simple.mock import MockClickAndDrop
from click_and_drop_api.simple.types import ManifestedOrders


@pytest.fixture
def api() -> MockClickAndDrop:
    return MockClickAndDrop()


def test_manifest_orders_returns_response(api: MockClickAndDrop) -> None:
    result = api.manifest_orders()
    assert isinstance(result, ManifestOrdersResponse)


def test_manifest_orders_has_manifest_number(api: MockClickAndDrop) -> None:
    result = api.manifest_orders()
    assert result.manifest_number is not None


def test_manifest_orders_with_carrier_name(api: MockClickAndDrop) -> None:
    result = api.manifest_orders(carrier_name="Royal Mail")
    assert isinstance(result, ManifestOrdersResponse)


def test_manifest_orders_increments_manifest_number(api: MockClickAndDrop) -> None:
    r1 = api.manifest_orders()
    r2 = api.manifest_orders()
    assert r2.manifest_number != r1.manifest_number


# --- .pdf property ---


def test_manifest_orders_pdf_returns_bytearray(api: MockClickAndDrop) -> None:
    result: ManifestedOrders = api.manifest_orders()
    assert isinstance(result.pdf, bytearray)


def test_manifest_orders_pdf_starts_with_pdf_header(api: MockClickAndDrop) -> None:
    result: ManifestedOrders = api.manifest_orders()
    assert result.pdf[:4] == bytearray(b"%PDF")


def test_manifest_orders_pdf_none_when_no_document() -> None:
    result = ManifestedOrders(manifest_number=1, document_pdf=None)
    assert result.pdf is None
