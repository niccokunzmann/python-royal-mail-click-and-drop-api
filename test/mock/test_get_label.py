"""Tests for MockClickAndDrop.get_label."""

import pytest

from click_and_drop_api.simple.mock import MockClickAndDrop

from .helpers import make_order


@pytest.mark.parametrize(
    "document_type", ["postageLabel", "despatchNote", "CN22", "CN23"]
)
@pytest.mark.parametrize("include_returns_label", [True, False, None])
@pytest.mark.parametrize("include_cn", [True, False, None])
def test_get_label_returns_pdf_bytes(
    api: MockClickAndDrop, document_type, include_returns_label, include_cn
):
    r = api.create_order(make_order())
    order_id = r.created_orders[0].order_identifier
    label = api.get_label(
        order_id,
        document_type=document_type,
        include_returns_label=include_returns_label,
        include_cn=include_cn,
    )
    assert isinstance(label, bytearray)
    assert label[:4] == bytearray(b"%PDF")
