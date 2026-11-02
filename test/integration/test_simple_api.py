"""The functions of the simple API, with the mock and the real API.

The account of the real API is an OLP account: not OBA, not ChannelShipper.
The mock is configured the same way.
Functions that change orders beyond the test orders are not tested here:
manifesting changes all eligible orders of the account.
"""

from datetime import timedelta

import pytest

from click_and_drop_api import ShipmentPackageRequest
from click_and_drop_api.exceptions import BadRequestException, ForbiddenException
from click_and_drop_api.simple import PostageDetails, ProductItem
from click_and_drop_api.simple.addresses import get_address

from .conftest import order


def references(orders) -> list[str]:
    return [o.order_reference for o in orders]


# ── version and account ────────────────────────────────────────────────────────


def test_get_version(api):
    version = api.get_version()
    assert version.release
    assert version.release_date is not None


def test_account_is_not_oba(api):
    assert api.is_oba() is False
    assert api.get_default_carrier_name() == "Royal Mail OLP"


def test_shipping_with_service_of_the_account(api):
    result = api.test_shipping("letter", "OLP1")
    assert result.is_success, result.failed_messages


@pytest.mark.parametrize(
    "package_size, service_code", [("largeLetter", "TPN24"), ("letter", "XXXX")]
)
def test_shipping_with_unknown_service(api, package_size, service_code):
    result = api.test_shipping(package_size, service_code)
    assert result.is_failure
    [message] = result.failed_messages
    assert "31" in message
    assert service_code in message


def test_service_code_not_available_is_rejected(api, reference):
    unavailable = order(reference())
    unavailable.postage_details = PostageDetails(service_code="TPN24")
    response = api.create_orders([unavailable])
    [failure] = response.failed_orders
    [error] = failure.errors
    assert error.error_code == 31
    assert error.fields[0].field_name == "PostageDetails.ServiceCode"
    assert error.fields[0].value == "TPN24"


def test_order_details_need_channel_shipper(api, reference, create):
    [identifier] = create(reference())
    with pytest.raises(ForbiddenException):
        api.get_order_details(identifier)


def test_labels_need_oba(api, reference, create):
    [identifier] = create(reference())
    with pytest.raises(ForbiddenException):
        api.get_label(identifier, "postageLabel", include_returns_label=False)


# ── create ─────────────────────────────────────────────────────────────────────


def test_create_order(api, reference):
    ref = reference()
    response = api.create_order(order(ref))
    assert response.success_count == 1
    assert response.errors_count == 0
    [created] = response.created_orders
    assert created.order_reference == ref
    assert created.order_identifier > 0
    assert created.created_on is not None


def test_create_several_orders(api, reference):
    refs = [reference() for _ in range(3)]
    response = api.create_orders([order(ref) for ref in refs])
    assert response.success_count == 3
    assert sorted(references(response.created_orders)) == sorted(refs)


def test_create_more_orders_than_one_request_takes(api, reference):
    api.max_order_count = 2
    refs = [reference() for _ in range(5)]
    response = api.create_orders([order(ref) for ref in refs])
    assert response.success_count == 5
    assert sorted(references(response.created_orders)) == sorted(refs)


def test_eu_order_needs_manufacturer_id(api, reference):
    eu = order(reference())
    eu.recipient.address = get_address("DK")
    eu.postage_details = PostageDetails(service_code="ITROLP")
    eu.packages = [
        ShipmentPackageRequest(
            weight_in_grams=100,
            package_format_identifier="largeLetter",
            contents=[
                ProductItem(
                    quantity=1,
                    unit_value=10.0,
                    unit_weight_in_grams=50,
                    customs_description="Mushroom Extract",
                    customs_code="1302199090",
                    origin_country_code="GB",
                    customs_declaration_category="eCommerceSaleOfGoods",
                )
            ],
        )
    ]
    response = api.create_orders([eu])
    [failure] = response.failed_orders
    codes = {e.error_code for e in failure.errors}
    assert 119 in codes, failure.errors
    fields = {f.field_name for e in failure.errors for f in e.fields or []}
    assert "Packages.Contents.NonStandardisedManufacturerId" in fields


# ── get ────────────────────────────────────────────────────────────────────────


def test_get_orders_by_identifier_and_reference(api, reference, create):
    refs = [reference(), reference()]
    identifiers = create(*refs)
    by_id = api.get_orders(identifiers)
    by_ref = api.get_orders(refs)
    assert sorted(references(by_id)) == sorted(refs)
    assert sorted(o.order_identifier for o in by_ref) == sorted(identifiers)


def test_get_order(api, reference, create):
    ref = reference()
    [identifier] = create(ref)
    assert api.get_order(identifier).order_reference == ref
    assert api.get_order(ref).order_identifier == identifier


def test_get_missing_order(api, reference, create):
    [identifier] = create(reference())
    api.delete_orders([identifier])
    assert api.get_order(identifier) is None
    with pytest.raises(BadRequestException) as error:
        api.get_orders([identifier])
    assert [e.code for e in error.value.data] == ["2", "1"]


def test_get_missing_identifier_next_to_existing_one(api, reference, create):
    existing, deleted = create(reference(), reference())
    api.delete_orders([deleted])
    assert [o.order_identifier for o in api.get_orders([deleted, existing])] == [
        existing
    ]


# ── list ───────────────────────────────────────────────────────────────────────


def test_iter_orders_newest_first(api, reference, create):
    before = api.now() - timedelta(seconds=1)
    refs = [reference(), reference()]
    create(*refs)
    listed = references(api.iter_orders(start=before))
    assert [ref for ref in listed if ref in refs] == list(reversed(refs))


def test_iter_orders_pages(api, reference, create):
    api.max_order_count = 2
    start = api.now() - timedelta(seconds=1)
    refs = [reference() for _ in range(5)]
    create(*refs)
    listed = [
        ref for ref in references(api.iter_recent_orders(until=start)) if ref in refs
    ]
    assert listed == list(reversed(refs))


def test_iter_orders_end_must_be_after_start(api):
    now = api.now()
    with pytest.raises(BadRequestException):
        list(api.iter_orders(start=now, end=now))


def test_iter_orders_in_the_future_is_empty(api):
    assert list(api.iter_orders(start=api.now() + timedelta(days=1))) == []


# ── delete ─────────────────────────────────────────────────────────────────────


def test_delete_by_identifier(api, reference, create):
    ref = reference()
    [identifier] = create(ref)
    result = api.delete_orders([identifier])
    assert [(o.order_identifier, o.order_reference) for o in result.deleted_orders] == [
        (identifier, ref)
    ]
    assert result.errors == []
    assert api.lookup_references([ref]).absent == {ref}


def test_delete_by_reference(api, reference, create):
    ref = reference()
    [identifier] = create(ref)
    result = api.delete_order(ref)
    assert [o.order_identifier for o in result.deleted_orders] == [identifier]


def test_delete_existing_and_missing(api, reference, create):
    ref = reference()
    [identifier] = create(ref)
    result = api.delete_orders([ref, reference()])
    assert [o.order_identifier for o in result.deleted_orders] == [identifier]
    assert [e.code for e in result.errors] == ["3", "1"]


def test_delete_more_orders_than_one_request_takes(api, reference, create):
    api.max_order_count = 2
    identifiers = create(*[reference() for _ in range(5)])
    result = api.delete_orders(identifiers)
    assert sorted(o.order_identifier for o in result.deleted_orders) == sorted(
        identifiers
    )


# ── status ─────────────────────────────────────────────────────────────────────


def test_set_status_of_new_order_to_new(api, reference, create):
    [identifier] = create(reference())
    response = api.set_order_status([identifier], "new")
    assert [o.order_identifier for o in response.updated_orders] == [identifier]
    assert not response.errors


# ── iterating while orders get deleted ─────────────────────────────────────────


def test_deleting_the_listed_orders_while_iterating(api, reference, create):
    """Each next page starts after the last listed order, so none is skipped."""
    api.max_order_count = 2
    start = api.now() - timedelta(seconds=1)
    refs = [reference() for _ in range(5)]
    identifiers = create(*refs)
    listed = []
    for info in api.iter_recent_orders(until=start):
        if info.order_identifier in identifiers:
            listed.append(info.order_identifier)
            api.delete_orders([info.order_identifier])
    assert listed == list(reversed(identifiers))


def test_orders_deleted_before_they_are_listed_are_left_out(api, reference, create):
    api.max_order_count = 2
    start = api.now() - timedelta(seconds=1)
    identifiers = create(*[reference() for _ in range(5)])
    oldest, newest = identifiers[0], identifiers[-1]
    listed = []
    for info in api.iter_recent_orders(until=start):
        if info.order_identifier in identifiers:
            listed.append(info.order_identifier)
            if info.order_identifier == newest:
                api.delete_orders([oldest])
    assert listed == list(reversed(identifiers[1:]))
