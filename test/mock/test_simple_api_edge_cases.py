"""Edge cases of the simple API that the other tests do not reach."""

from unittest.mock import Mock, patch

import pytest

import click_and_drop_api
from click_and_drop_api.exceptions import ApiException, BadRequestException
from click_and_drop_api.models.error_response import ErrorResponse
from click_and_drop_api.simple import (
    ClickAndDrop,
    MockClickAndDrop,
    ReplaceDuplicateReferences,
)
from click_and_drop_api.simple.addresses import get_all_country_codes
from click_and_drop_api.simple.api import order_identifiers_to_string

from .helpers import make_order

KEY = "a" * 36


def bad_request(data) -> BadRequestException:
    return BadRequestException(status=400, reason="Bad Request", body="", data=data)


# ── from_env ───────────────────────────────────────────────────────────────────


def test_from_env(monkeypatch):
    monkeypatch.setenv("MY_KEY", KEY)
    assert MockClickAndDrop.from_env("MY_KEY").key == KEY


def test_from_env_without_variable(monkeypatch):
    monkeypatch.delenv("MY_KEY", raising=False)
    with pytest.raises(KeyError):
        MockClickAndDrop.from_env("MY_KEY")


# ── identifiers in the URL ─────────────────────────────────────────────────────


def test_identifiers_in_url():
    """References are quoted and URL encoded, identifiers are numbers."""
    assert order_identifiers_to_string([1, "a;b"]) == '1;"a%3Bb"'


def test_identifier_of_wrong_type():
    with pytest.raises(TypeError):
        order_identifiers_to_string([1.5])


# ── replace_orders ─────────────────────────────────────────────────────────────


def test_replace_a_single_order(api: MockClickAndDrop):
    response = api.replace_orders(make_order("ref"))
    assert [o.order_reference for o in response.created_orders] == ["ref"]


# ── lookup_references ──────────────────────────────────────────────────────────


def test_lookup_raises_other_bad_requests(api: MockClickAndDrop):
    with patch.object(
        api, "_get_orders", side_effect=bad_request(ErrorResponse(message="x"))
    ):
        with pytest.raises(BadRequestException):
            api.lookup_references(["ref"])


def test_lookup_raises_errors_about_other_references(api: MockClickAndDrop):
    """Without progress, the lookup would never end."""
    error = click_and_drop_api.OrderErrorResponse(
        channel_order_reference="other", code="3", message="missing"
    )
    with patch.object(api, "_get_orders", side_effect=bad_request([error])):
        with pytest.raises(BadRequestException):
            api.lookup_references(["ref"])


def test_lookup_without_error_and_without_order(api: MockClickAndDrop):
    with patch.object(api, "_get_orders", return_value=[]):
        assert api.lookup_references(["ref"]).absent == {"ref"}


# ── get_order_details ──────────────────────────────────────────────────────────


def test_order_details_of_ambiguous_reference(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    api.create_order(make_order("ref"))
    with pytest.raises(BadRequestException):
        api.get_order_details("ref")


# ── test_shipping and get_countries_for_shipping ───────────────────────────────


def test_shipping_needs_an_address(api: MockClickAndDrop):
    with pytest.raises(ValueError):
        api.test_shipping("letter", "OLP1", address=[])


@pytest.mark.parametrize(
    "error, message",
    [
        (
            ApiException(status=500, reason="Server Error"),
            "API error (500 Server Error)",
        ),
        (RuntimeError("boom"), "Unexpected error: boom"),
    ],
)
def test_shipping_reports_errors_while_creating_orders(
    api: MockClickAndDrop, error, message
):
    with patch.object(api, "create_orders", side_effect=error):
        result = api.test_shipping("letter", "OLP1", address=["GB", "DE"])
    assert result.failed_countries == ["GB", "DE"]
    assert result.successful_countries == []
    assert all(m.startswith(message) for m in result.failed_messages)


def test_countries_for_shipping():
    api = MockClickAndDrop(is_oba=False)
    assert api.get_countries_for_shipping("letter", "OLP1") == get_all_country_codes()
    assert api.get_countries_for_shipping("letter", "TPN24") == []
    assert list(api.iter_orders()) == [], "the test orders are deleted"


# ── delete_orders_with_references ──────────────────────────────────────────────────────────────


def test_copy_deleted_at_the_same_time_is_no_failure(api: MockClickAndDrop):
    """Click & Drop reports an order that is already deleted (code 2) and the request (code 1)."""
    api.create_order(make_order("ref"))
    [old] = [o.order_identifier for o in api.iter_orders()]
    gone = click_and_drop_api.DeleteOrdersResource(
        deleted_orders=[],
        errors=[
            click_and_drop_api.OrderErrorInfo(
                order_identifier=old, code="2", message="gone"
            ),
            click_and_drop_api.OrderErrorInfo(
                order_reference=str(old), code="1", message="invalid"
            ),
        ],
    )
    with patch.object(api, "delete_orders", return_value=gone):
        response = api.create_orders(
            [make_order("ref")], strategy=ReplaceDuplicateReferences()
        )
    assert response.failed_orders == []
    assert [o.order_reference for o in response.created_orders] == ["ref"]


# ── ClickAndDrop passes requests on ────────────────────────────────────────────


def test_manifest_request_is_passed_on():
    """Manifesting is not tested against Click & Drop: it manifests all orders of the account."""
    api = ClickAndDrop(KEY)
    api._manifests_api = Mock()
    request = object()
    assert (
        api._manifest_orders(request)
        is api._manifests_api.manifest_eligible_async.return_value
    )
    api._manifests_api.manifest_eligible_async.assert_called_once_with(request)
