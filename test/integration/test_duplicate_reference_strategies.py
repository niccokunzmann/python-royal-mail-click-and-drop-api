"""The strategies against duplicate references, with the mock and the real API.

The same tests run against both, so they also check that the mock behaves like Click & Drop.
Duplicates are created with the ``create`` fixture: each order in its own request,
like a checkout that is retried.
"""

import pytest

from click_and_drop_api.exceptions import BadRequestException
from click_and_drop_api.simple import (
    NullStrategy,
    RejectDuplicateReferences,
    ReplaceDuplicateReferences,
    StrategyErrorCode,
)

from .conftest import order


def copies(api, ref: str) -> list[int]:
    """The identifiers of the orders with this reference (at least two if duplicated)."""
    return sorted(o.order_identifier for o in api.find_orders_by_reference([ref])[ref])


def upload(api, refs: list[str], strategy):
    """Upload the orders in one request."""
    return api.create_orders([order(ref) for ref in refs], strategy=strategy)


def created(response) -> list[str]:
    return sorted(o.order_reference for o in response.created_orders)


def failed(response) -> dict[str, int]:
    return {
        f.order.order_reference: f.errors[0].error_code for f in response.failed_orders
    }


# ── the API ────────────────────────────────────────────────────────────────────


def test_same_reference_in_one_request_is_rejected(api, reference):
    ref, other = reference(), reference()
    response = upload(api, [ref, ref, other], NullStrategy())
    assert created(response) == [other]
    assert failed(response) == {ref: 76}
    assert response.errors_count == 2
    [error] = response.failed_orders[0].errors
    assert error.fields[0].field_name == "OrderReference"


def test_duplicate_reference_is_ambiguous(api, reference, create):
    ref = reference()
    identifiers = create(ref, ref)
    with pytest.raises(BadRequestException) as error:
        api.get_orders(ref)
    assert [(e.channel_order_reference, e.code) for e in error.value.data] == [
        (ref, "5"),
        (f'"{ref}"', "1"),
    ]
    assert api.lookup_references([ref]).ambiguous == {ref}
    assert copies(api, ref) == sorted(identifiers)


def test_missing_reference(api, reference):
    ref = reference()
    with pytest.raises(BadRequestException) as error:
        api.get_orders(ref)
    assert [(e.channel_order_reference, e.code) for e in error.value.data] == [
        (ref, "3"),
        (f'"{ref}"', "1"),
    ]
    assert api.get_order(ref) is None
    assert api.lookup_references([ref]).absent == {ref}


def test_missing_reference_next_to_existing_one(api, reference, create):
    missing, existing = reference(), reference()
    create(existing)
    assert [o.order_reference for o in api.get_orders([missing, existing])] == [
        existing
    ]


def test_delete_missing_order(api, reference, create):
    ref = reference()
    [identifier] = create(ref)
    assert [
        o.order_identifier for o in api.delete_orders([identifier]).deleted_orders
    ] == [identifier]
    result = api.delete_orders([identifier, ref])
    assert result.deleted_orders == []
    assert [e.code for e in result.errors] == ["2", "3", "1"]


def test_delete_ambiguous_reference_deletes_nothing(api, reference, create):
    ref = reference()
    identifiers = create(ref, ref)
    with pytest.raises(BadRequestException) as error:
        api.delete_orders(ref)
    assert [e.code for e in error.value.data if e.code != "1"] == ["22", "23", "23"]
    assert sorted(
        e.order_identifier for e in error.value.data if e.code == "23"
    ) == sorted(identifiers)
    assert copies(api, ref) == sorted(identifiers)


def test_orders_are_listed_newest_first(api, reference, create):
    refs = [reference() for _ in range(3)]
    create(*refs)
    listed = [
        o.order_reference for o in api.iter_recent_orders() if o.order_reference in refs
    ]
    assert listed == list(reversed(refs))


# ── NullStrategy ───────────────────────────────────────────────────────────────


def test_null_strategy_uploads_duplicates(api, reference, create):
    ref = reference()
    create(ref)
    response = upload(api, [ref], NullStrategy())
    assert created(response) == [ref]
    assert api.lookup_references([ref]).ambiguous == {ref}


# ── RejectDuplicateReferences ──────────────────────────────────────────────────


def test_reject_new_reference_is_uploaded(api, reference):
    ref = reference()
    response = upload(api, [ref], RejectDuplicateReferences())
    assert created(response) == [ref]


def test_reject_existing_reference(api, reference, create):
    existing, new = reference(), reference()
    [identifier] = create(existing)
    response = upload(api, [existing, new], RejectDuplicateReferences())
    assert failed(response) == {existing: StrategyErrorCode.DUPLICATE_REFERENCE}
    assert created(response) == [new]
    assert copies(api, existing) == [identifier]


def test_reject_existing_duplicates(api, reference, create):
    ref = reference()
    identifiers = create(ref, ref)
    response = upload(api, [ref], RejectDuplicateReferences())
    assert failed(response) == {ref: StrategyErrorCode.DUPLICATE_REFERENCE}
    assert copies(api, ref) == sorted(identifiers)


def test_reject_same_reference_in_one_upload(api, reference):
    ref = reference()
    response = upload(api, [ref, ref], RejectDuplicateReferences())
    assert failed(response) == {ref: StrategyErrorCode.DUPLICATE_REFERENCE}
    assert response.errors_count == 2
    assert api.lookup_references([ref]).absent == {ref}


# ── ReplaceDuplicateReferences ─────────────────────────────────────────────────


def test_replace_new_reference_is_uploaded(api, reference):
    ref = reference()
    response = upload(api, [ref], ReplaceDuplicateReferences())
    assert created(response) == [ref]
    assert api.lookup_references([ref]).unique == {ref}


def test_replace_existing_order(api, reference, create):
    ref = reference()
    [old] = create(ref)
    response = upload(api, [ref], ReplaceDuplicateReferences())
    assert created(response) == [ref]
    [new] = copies(api, ref)
    assert new != old


@pytest.mark.parametrize("number", [2, 3])
def test_replace_existing_duplicates(api, reference, create, number):
    ref, other = reference(), reference()
    old = create(*[ref] * number, other)
    response = upload(api, [ref], ReplaceDuplicateReferences())
    assert created(response) == [ref]
    [new] = copies(api, ref)
    assert new not in old
    assert copies(api, other) == [old[-1]], "other orders are not touched"


def test_replace_same_reference_in_one_upload(api, reference):
    ref, other = reference(), reference()
    response = upload(api, [ref, ref, other], ReplaceDuplicateReferences())
    assert failed(response) == {ref: StrategyErrorCode.DUPLICATE_REFERENCE}
    assert created(response) == [other]


# ── references with different states in one request ───────────────────────────


def test_ambiguous_reference_next_to_unique_one_is_left_out(api, reference, create):
    """Click & Drop does not report the duplicate if another order is found."""
    ambiguous, unique = reference(), reference()
    create(ambiguous, ambiguous, unique)
    assert [o.order_reference for o in api.get_orders([ambiguous, unique])] == [unique]


def test_lookup_finds_all_states_in_one_call(api, reference, create):
    ambiguous, unique, missing = reference(), reference(), reference()
    create(ambiguous, ambiguous, unique)
    lookup = api.lookup_references([ambiguous, missing, unique])
    assert lookup.ambiguous == {ambiguous}
    assert lookup.unique == {unique}
    assert lookup.absent == {missing}


def test_replace_several_references_with_duplicates(api, reference, create):
    duplicated, single, new = reference(), reference(), reference()
    old = create(duplicated, duplicated, single)
    response = upload(api, [duplicated, single, new], ReplaceDuplicateReferences())
    assert created(response) == sorted([duplicated, single, new])
    for ref in (duplicated, single, new):
        [identifier] = copies(api, ref)
        assert identifier not in old


# ── replace_orders ─────────────────────────────────────────────────────────────


def test_replace_orders_without_duplicates_needs_two_requests(api, reference):
    refs = [reference() for _ in range(3)]
    api.requests.clear()
    response = api.replace_orders([order(ref) for ref in refs])
    assert created(response) == sorted(refs)
    assert api.requests == {"create": 1, "get": 1}, "one upload, one lookup"


def test_replace_orders_in_batches(api, reference):
    api.max_order_count = 2
    refs = [reference() for _ in range(5)]
    api.requests.clear()
    response = api.replace_orders([order(ref) for ref in refs])
    assert created(response) == sorted(refs)
    assert api.requests == {"create": 3, "get": 3}


def test_replace_orders_replaces_existing_order(api, reference, create):
    ref, new = reference(), reference()
    [old] = create(ref)
    response = api.replace_orders([order(ref), order(new)])
    assert created(response) == sorted([ref, new])
    [kept] = copies(api, ref)
    assert kept != old
    assert kept in [o.order_identifier for o in response.created_orders]


@pytest.mark.parametrize("number", [2, 3])
def test_replace_orders_removes_all_duplicates(api, reference, create, number):
    ref, other = reference(), reference()
    old = create(*[ref] * number, other)
    response = api.replace_orders([order(ref)])
    assert created(response) == [ref]
    [kept] = copies(api, ref)
    assert kept not in old
    assert copies(api, other) == [old[-1]], "other orders are not touched"


def test_replace_orders_same_reference_twice(api, reference):
    ref, other = reference(), reference()
    response = api.replace_orders([order(ref), order(ref), order(other)])
    assert created(response) == [other]
    assert failed(response) == {ref: 76}
    assert api.lookup_references([ref]).absent == {ref}


# ── delete_orders_with_references ──────────────────────────────────────────────


@pytest.mark.parametrize("number", [1, 2, 3])
def test_delete_orders_with_references_searches_all_orders(
    api, reference, create, number
):
    ref, other = reference(), reference()
    old = create(*[ref] * number, other)
    assert api.delete_orders_with_references([ref]) == {}
    assert api.lookup_references([ref]).absent == {ref}
    assert copies(api, other) == [old[-1]], "other orders are not touched"


def test_delete_orders_with_references_keeps_orders(api, reference, create):
    ref = reference()
    first, second, third = create(ref, ref, ref)
    assert api.delete_orders_with_references([ref], keep=[second]) == {}
    assert copies(api, ref) == [second]


def test_delete_orders_with_no_references(api):
    api.requests.clear()
    assert api.delete_orders_with_references([]) == {}
    assert api.requests == {}
