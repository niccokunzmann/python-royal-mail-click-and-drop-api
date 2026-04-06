"""Tests for OrderInfo.tracking_link."""

from datetime import datetime, timezone


from click_and_drop_api.simple.types import OrderInfo

_T1 = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
_BASE_URL = "https://www.royalmail.com/track-your-item#/tracking-results/"


def _make(tracking_number=None) -> OrderInfo:
    return OrderInfo(
        order_identifier=1, created_on=_T1, tracking_number=tracking_number
    )


def test_tracking_link_none_when_no_tracking_number():
    assert _make().tracking_link is None


def test_tracking_link_contains_tracking_number():
    order = _make(tracking_number="AB000000001GB")
    assert "AB000000001GB" in order.tracking_link


def test_tracking_link_format():
    order = _make(tracking_number="AB000000001GB")
    assert order.tracking_link == _BASE_URL + "AB000000001GB"


def test_tracking_link_uses_actual_tracking_number():
    order = _make(tracking_number="FI964460579GB")
    assert order.tracking_link == _BASE_URL + "FI964460579GB"
