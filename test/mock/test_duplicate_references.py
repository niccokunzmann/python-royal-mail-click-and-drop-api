"""Duplicate order references and the strategies that prevent them.

Strategies do not raise: rejected orders are in ``failed_orders`` of the result.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest

import click_and_drop_api
from click_and_drop_api.exceptions import BadRequestException
from click_and_drop_api.simple import (
    ClickAndDrop,
    ClickAndDropError,
    InvalidDimensions,
    InvalidWeight,
    MockClickAndDrop,
    NullStrategy,
    ReferenceLookup,
    RejectDuplicateReferences,
    ReplaceDuplicateReferences,
    StrategyErrorCode,
)

from .helpers import make_order

KEY = "a" * 36


def create_each(api: MockClickAndDrop, orders) -> None:
    """Upload each order in its own request.

    Click & Drop rejects the same reference twice in one request (error 76),
    so duplicates arise from separate requests.
    """
    for order in orders:
        api.create_order(order)


def identifiers(api: MockClickAndDrop, reference: str) -> list[int]:
    return [o.order_identifier for o in api.find_orders_by_reference([reference])[reference]]


def created(response) -> list[str]:
    return [o.order_reference for o in response.created_orders]


def failed(response) -> dict[str, int]:
    """Map the reference of each failed order to its error code."""
    return {f.order.order_reference: f.errors[0].error_code for f in response.failed_orders}


def label(api: MockClickAndDrop, reference: str):
    api.get_label(reference, "postageLabel", include_returns_label=False)


@pytest.fixture
def replace() -> ReplaceDuplicateReferences:
    return ReplaceDuplicateReferences()


@pytest.fixture
def reject() -> RejectDuplicateReferences:
    return RejectDuplicateReferences()


# ── the problem: Click & Drop accepts duplicate references ────────────────────


def test_null_strategy_is_the_default():
    assert isinstance(MockClickAndDrop().create_order_strategy, NullStrategy)
    assert isinstance(ClickAndDrop(KEY).create_order_strategy, NullStrategy)


def test_null_strategy_uploads_duplicates(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    api.create_order(make_order("ref"))
    assert len(identifiers(api, "ref")) == 2


def test_get_orders_rejects_ambiguous_reference(api: MockClickAndDrop):
    create_each(api, [make_order("ref"), make_order("ref")])
    with pytest.raises(BadRequestException) as error:
        api.get_orders("ref")
    ambiguous, quoted = error.value.data
    assert ambiguous.code == "5"
    assert ambiguous.channel_order_reference == "ref"
    assert "Ambiguous reference" in ambiguous.message
    assert quoted.code == "1"
    assert quoted.channel_order_reference == '"ref"'


def test_get_orders_rejects_missing_reference(api: MockClickAndDrop):
    with pytest.raises(BadRequestException) as error:
        api.get_orders("missing")
    assert [e.code for e in error.value.data] == ["3", "1"]


def test_get_orders_leaves_out_missing_reference_next_to_existing(api: MockClickAndDrop):
    api.max_order_count = 100  # both references in one request
    api.create_order(make_order("ref"))
    assert [o.order_reference for o in api.get_orders(["missing", "ref"])] == ["ref"]


def test_get_order_returns_none_for_missing_reference(api: MockClickAndDrop):
    assert api.get_order("missing") is None


def test_get_order_raises_for_ambiguous_reference(api: MockClickAndDrop):
    create_each(api, [make_order("ref"), make_order("ref")])
    with pytest.raises(BadRequestException):
        api.get_order("ref")


def test_delete_ambiguous_reference_deletes_nothing(api: MockClickAndDrop):
    create_each(api, [make_order("ref"), make_order("ref")])
    with pytest.raises(BadRequestException) as error:
        api.delete_orders("ref")
    codes = [(e.code, e.order_identifier) for e in error.value.data]
    assert codes == [("22", None), ("23", 1), ("23", 2)]
    assert len(identifiers(api, "ref")) == 2


# ── find_orders_by_reference and iter_orders ──────────────────────────────────


def test_find_orders_by_reference(api: MockClickAndDrop):
    create_each(api, [make_order("one"), make_order("two"), make_order("two")])
    found = api.find_orders_by_reference(["one", "two", "missing"])
    assert [o.order_reference for o in found["one"]] == ["one"]
    assert [o.order_reference for o in found["two"]] == ["two", "two"]
    assert found["missing"] == []


def test_find_ambiguous_reference_only_since(api: MockClickAndDrop):
    create_each(api, [make_order("ref"), make_order("ref")])
    assert api.find_orders_by_reference(["ref"], since=api.now() + timedelta(1)) == {
        "ref": []
    }


def test_iter_orders_pages_through_all_orders(api: MockClickAndDrop):
    api.max_order_count = 2
    create_each(api, [make_order(f"ref-{i}") for i in range(5)])
    assert [o.order_reference for o in api.iter_orders()] == [
        f"ref-{i}" for i in reversed(range(5))
    ], "newest first"


def test_iter_orders_filters_by_time(api: MockClickAndDrop):
    api.create_order(make_order("old"))
    advance(api, timedelta(seconds=10))
    middle = api.now() + timedelta(milliseconds=500)
    api.create_order(make_order("new"))
    assert [o.order_reference for o in api.iter_orders(start=middle)] == ["new"]
    assert [o.order_reference for o in api.iter_orders(end=middle)] == ["old"]


def test_iter_orders_cuts_times_to_seconds(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    created = api.find_orders_by_reference(["ref"])["ref"][0].created_on
    start = created.replace(microsecond=0) + timedelta(milliseconds=999)
    assert [o.order_reference for o in api.iter_orders(start=start)] == ["ref"]
    assert list(api.iter_orders(end=created + timedelta(milliseconds=999))) == []


@pytest.mark.parametrize("seconds", [0, 0.5, -1])
def test_iter_orders_end_must_be_a_second_after_start(api: MockClickAndDrop, seconds):
    start = api.now()
    with pytest.raises(BadRequestException) as error:
        list(api.iter_orders(start=start, end=start + timedelta(seconds=seconds)))
    assert "should be greater than" in error.value.body


def test_find_stops_when_two_orders_of_each_reference_are_found(api: MockClickAndDrop):
    api.max_order_count = 1
    create_each(api, [make_order(f"earlier-{i}") for i in range(10)])
    create_each(api, [make_order("ref"), make_order("ref")])
    found = api.find_orders_by_reference(["ref"])
    assert len(found["ref"]) == 2
    assert len(api.page_requests) == 2, "only the pages until both orders are found"


def test_find_continues_with_given_orders(api: MockClickAndDrop):
    create_each(api, [make_order("ref")] * 4)
    orders = api.iter_orders()
    first = api.find_orders_by_reference(["ref"], orders=orders)
    second = api.find_orders_by_reference(["ref"], orders=orders)
    assert [o.order_identifier for o in first["ref"]] == [4, 3]
    assert [o.order_identifier for o in second["ref"]] == [2, 1]


def test_lookup_references(api: MockClickAndDrop):
    create_each(api, [make_order("once"), make_order("twice"), make_order("twice")])
    lookup = api.lookup_references(["once", "twice", "missing", "once"])
    assert lookup.absent == {"missing"}
    assert lookup.unique == {"once"}
    assert lookup.ambiguous == {"twice"}
    assert lookup.existent == {"once", "twice"}
    assert lookup.orders["once"].order_reference == "once"
    assert list(lookup.orders) == ["once"]
    assert len(api.page_requests) == 0, "does not list orders"


def test_lookup_only_absent_references(api: MockClickAndDrop):
    lookup = api.lookup_references(["a", "b"])
    assert lookup == ReferenceLookup(absent={"a", "b"})
    assert lookup.existent == set()


def test_lookup_only_ambiguous_references(api: MockClickAndDrop):
    create_each(api, [make_order("ref"), make_order("ref")])
    assert api.lookup_references(["ref"]) == ReferenceLookup(ambiguous={"ref"})


def test_deleting_does_not_skip_orders_while_paging(api: MockClickAndDrop):
    api.max_order_count = 2
    create_each(api, [make_order(f"ref-{i}") for i in range(6)])
    seen = []
    for info in api.iter_orders():
        seen.append(info.order_reference)
        api.delete_orders([info.order_identifier])
    assert seen == [f"ref-{i}" for i in reversed(range(6))]


def advance(api: MockClickAndDrop, delta: timedelta):
    api._MockClickAndDrop__now += delta


def test_recent_orders_come_first(api: MockClickAndDrop):
    api.create_order(make_order("old"))
    advance(api, timedelta(days=10))
    api.create_order(make_order("new"))
    assert [o.order_reference for o in api.iter_recent_orders()][:2] == ["new", "old"]


def test_recent_orders_are_listed_once(api: MockClickAndDrop):
    api.max_order_count = 2
    for _ in range(6):
        api.create_order(make_order("ref"))
        advance(api, timedelta(hours=7))
    orders = [o.order_identifier for o in api.iter_recent_orders()]
    assert sorted(orders) == [1, 2, 3, 4, 5, 6]
    assert len(set(api.page_requests)) == len(api.page_requests), "no page twice"


def test_recent_duplicates_do_not_list_old_orders(api: MockClickAndDrop):
    create_each(api, [make_order(f"old-{i}") for i in range(20)])
    advance(api, timedelta(days=100))
    create_each(api, [make_order("ref"), make_order("ref")])
    found = api.find_orders_by_reference(["ref"])
    assert len(found["ref"]) == 2
    assert len(api.page_requests) == -(-2 // api.max_order_count), "the newest pages only"


@pytest.mark.parametrize("copies", [2, 3, 5])
def test_replace_lists_each_time_span_once(api: MockClickAndDrop, replace, copies):
    api.max_order_count = 2
    create_each(api, [make_order(f"old-{i}") for i in range(20)])
    advance(api, timedelta(days=100))
    for _ in range(copies):
        api.create_order(make_order("ref"))
        advance(api, timedelta(hours=10))
    api.page_requests.clear()
    response = api.create_orders([make_order("ref")], strategy=replace)
    assert created(response) == ["ref"]
    assert len(identifiers(api, "ref")) == 1
    assert len(set(api.page_requests)) == len(api.page_requests), "no page twice"
    assert len(api.page_requests) <= copies // 2 + 1, "only the pages with copies"


# ── empty arguments ────────────────────────────────────────────────────────────


def test_empty_arguments(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    assert api.find_orders_by_reference([]) == {}
    assert api.lookup_references([]) == ReferenceLookup()
    assert api.get_orders([]) == []
    assert api.delete_orders([]).deleted_orders == []
    assert len(api.page_requests) == 0
    assert len(identifiers(api, "ref")) == 1


# ── choosing the strategy ──────────────────────────────────────────────────────


def test_strategy_from_constructor(replace):
    assert MockClickAndDrop(create_order_strategy=replace).create_order_strategy is replace
    assert ClickAndDrop(KEY, create_order_strategy=replace).create_order_strategy is replace


def test_strategy_set_on_api_is_used(replace):
    api = MockClickAndDrop(create_order_strategy=replace)
    api.create_order(make_order("ref"))
    api.create_order(make_order("ref"))
    assert len(identifiers(api, "ref")) == 1


def test_null_strategy_argument_overrides_api_strategy(replace):
    api = MockClickAndDrop(create_order_strategy=replace)
    api.create_order(make_order("ref"))
    api.create_orders([make_order("ref")], strategy=NullStrategy())
    assert len(identifiers(api, "ref")) == 2


@pytest.mark.parametrize("strategy", [NullStrategy(), RejectDuplicateReferences(), ReplaceDuplicateReferences()])
def test_empty_upload(api: MockClickAndDrop, strategy):
    response = api.create_orders([], strategy=strategy)
    assert response.success_count == response.errors_count == 0


# ── ReplaceDuplicateReferences ─────────────────────────────────────────────────


def test_new_order_is_uploaded(api: MockClickAndDrop, replace):
    response = api.create_orders([make_order("ref")], strategy=replace)
    assert created(response) == ["ref"]
    assert len(identifiers(api, "ref")) == 1


def test_existing_order_is_replaced(api: MockClickAndDrop, replace):
    api.create_order(make_order("ref"))
    [old] = identifiers(api, "ref")
    response = api.create_orders([make_order("ref")], strategy=replace)
    assert created(response) == ["ref"]
    [new] = identifiers(api, "ref")
    assert new != old


def test_existing_duplicates_are_cleaned_up(api: MockClickAndDrop, replace):
    create_each(api, [make_order("ref"), make_order("ref"), make_order("other")])
    api.create_orders([make_order("ref")], strategy=replace)
    assert len(identifiers(api, "ref")) == 1
    assert len(identifiers(api, "other")) == 1


def test_all_duplicates_are_found_by_default(api: MockClickAndDrop, replace):
    create_each(api, [make_order("ref"), make_order("ref")])
    with patch.object(api, "now", return_value=api.now() + timedelta(days=3650)):
        api.create_orders([make_order("ref")], strategy=replace)
    assert len(list(api.iter_orders())) == 1


def test_lookback_limits_search_for_duplicates(api: MockClickAndDrop):
    create_each(api, [make_order("ref"), make_order("ref")])
    replace = ReplaceDuplicateReferences(lookback=timedelta(days=60))
    with patch.object(api, "now", return_value=api.now() + timedelta(days=61)):
        api.create_orders([make_order("ref")], strategy=replace)
    assert len(list(api.iter_orders())) == 3, "old duplicates were not found"


@pytest.mark.parametrize("copies", [2, 3, 5])
def test_all_copies_are_replaced(api: MockClickAndDrop, replace, copies):
    api.max_order_count = 2
    create_each(api, [make_order("ref")] * copies + [make_order("other")])
    response = api.create_orders([make_order("ref")], strategy=replace)
    assert created(response) == ["ref"]
    assert len(identifiers(api, "ref")) == 1
    assert len(identifiers(api, "other")) == 1


def test_replace_stops_paging_early(api: MockClickAndDrop, replace):
    api.max_order_count = 1
    create_each(api, [make_order(f"earlier-{i}") for i in range(10)])
    create_each(api, [make_order("ref"), make_order("ref")])
    api.page_requests.clear()
    api.create_orders([make_order("ref")], strategy=replace)
    assert len(api.page_requests) == 2
    assert len(identifiers(api, "ref")) == 1


def test_replace_single_order_does_not_list_orders(api: MockClickAndDrop, replace):
    api.create_order(make_order("ref"))
    api.create_orders([make_order("ref")], strategy=replace)
    assert len(api.page_requests) == 0


def test_reject_does_not_list_orders(api: MockClickAndDrop, reject):
    create_each(api, [make_order("ref"), make_order("ref")])
    api.create_orders([make_order("ref")], strategy=reject)
    assert len(api.page_requests) == 0


def test_manifested_third_copy_is_found(api: MockClickAndDrop, replace):
    create_each(api, [make_order("ref")] * 3)
    [_, _, third] = [o.order_identifier for o in api.iter_orders()]
    api._orders[third].manifested_on = api.now()  # only the third copy
    response = api.create_orders([make_order("ref")], strategy=replace)
    assert failed(response) == {"ref": StrategyErrorCode.ORDER_MANIFESTED}
    assert identifiers(api, "ref") == [third]


@pytest.mark.parametrize("strategy", [RejectDuplicateReferences(), ReplaceDuplicateReferences()])
def test_same_reference_twice_in_one_upload(api: MockClickAndDrop, strategy):
    response = api.create_orders(
        [make_order("ref"), make_order("ref"), make_order("other")], strategy=strategy
    )
    assert created(response) == ["other"]
    assert [f.order.order_reference for f in response.failed_orders] == ["ref", "ref"]
    assert failed(response) == {"ref": StrategyErrorCode.DUPLICATE_REFERENCE}
    assert response.success_count == 1
    assert response.errors_count == 2


def test_printed_label_is_not_cancelled(api: MockClickAndDrop, replace):
    create_each(api, [make_order("ref"), make_order("other")])
    [printed] = identifiers(api, "ref")
    label(api, "ref")
    response = api.create_orders([make_order("ref"), make_order("other")], strategy=replace)
    assert failed(response) == {"ref": StrategyErrorCode.LABEL_ALREADY_PRINTED}
    assert created(response) == ["other"], "the other order goes on"
    assert identifiers(api, "ref") == [printed]


def test_printed_label_is_deleted_if_allowed(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    [old] = identifiers(api, "ref")
    label(api, "ref")
    response = api.create_orders(
        [make_order("ref")], strategy=ReplaceDuplicateReferences(delete_printed=True)
    )
    assert created(response) == ["ref"]
    [new] = identifiers(api, "ref")
    assert new != old


@pytest.mark.parametrize("delete_printed", [True, False])
def test_manifested_order_is_not_deleted(api: MockClickAndDrop, delete_printed):
    api.create_order(make_order("ref"))
    label(api, "ref")
    api.manifest_orders()
    response = api.create_orders(
        [make_order("ref"), make_order("other")],
        strategy=ReplaceDuplicateReferences(delete_printed=delete_printed),
    )
    assert failed(response) == {"ref": StrategyErrorCode.ORDER_MANIFESTED}
    assert created(response) == ["other"]
    assert len(identifiers(api, "ref")) == 1


def test_failed_order_has_message_and_field(api: MockClickAndDrop, replace):
    api.create_order(make_order("ref"))
    label(api, "ref")
    api.manifest_orders()
    [failure] = api.create_orders([make_order("ref")], strategy=replace).failed_orders
    [error] = failure.errors
    assert "manifested" in error.error_message
    assert error.fields[0].field_name == "orderReference"
    assert error.fields[0].value == "ref"


def test_delete_failure_rejects_only_that_order(api: MockClickAndDrop, replace):
    create_each(api, [make_order("ref"), make_order("other")])
    [ref_id] = identifiers(api, "ref")
    delete = api.delete_orders

    def delete_all_but_ref(order_identifiers):
        result = delete([i for i in order_identifiers if i != ref_id])
        result.errors.append(
            click_and_drop_api.OrderErrorInfo(order_identifier=ref_id, code="X", message="nope")
        )
        return result

    with patch.object(api, "delete_orders", side_effect=delete_all_but_ref):
        response = api.create_orders(
            [make_order("ref"), make_order("other")], strategy=replace
        )
    assert failed(response) == {"ref": StrategyErrorCode.DELETE_FAILED}
    assert "X: nope" in response.failed_orders[0].errors[0].error_message
    assert created(response) == ["other"]
    assert identifiers(api, "ref") == [ref_id]


def test_strategy_failures_and_click_and_drop_failures_are_combined(api: MockClickAndDrop, replace):
    """A Click & Drop rejection still appears next to the strategy's rejections."""
    api.create_order(make_order("printed"))
    label(api, "printed")
    api.manifest_orders()
    with patch.object(api, "_validate_order", side_effect=lambda o: (
        [click_and_drop_api.CreateOrderErrorResponse(error_code=119, error_message="m")]
        if o.order_reference == "bad" else []
    )):
        response = api.create_orders(
            [make_order("printed"), make_order("bad"), make_order("good")], strategy=replace
        )
    assert created(response) == ["good"]
    assert failed(response) == {
        "printed": StrategyErrorCode.ORDER_MANIFESTED,
        "bad": 119,
    }
    assert response.errors_count == 2


# ── RejectDuplicateReferences ──────────────────────────────────────────────────


def test_reject_uploads_new_reference(api: MockClickAndDrop, reject):
    response = api.create_orders([make_order("ref")], strategy=reject)
    assert created(response) == ["ref"]


def test_reject_existing_reference(api: MockClickAndDrop, reject):
    api.create_order(make_order("ref"))
    [old] = identifiers(api, "ref")
    response = api.create_orders([make_order("ref"), make_order("other")], strategy=reject)
    assert failed(response) == {"ref": StrategyErrorCode.DUPLICATE_REFERENCE}
    assert created(response) == ["other"]
    assert identifiers(api, "ref") == [old], "nothing deleted"


def test_reject_existing_duplicates(api: MockClickAndDrop, reject):
    create_each(api, [make_order("ref"), make_order("ref")])
    response = api.create_orders([make_order("ref")], strategy=reject)
    assert failed(response) == {"ref": StrategyErrorCode.DUPLICATE_REFERENCE}
    assert len(identifiers(api, "ref")) == 2


# ── mock: manifested orders cannot be deleted ──────────────────────────────────


def test_mock_does_not_delete_manifested_orders(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    label(api, "ref")
    api.manifest_orders()
    result = api.delete_orders("ref")
    assert result.deleted_orders == []
    assert [e.order_reference for e in result.errors] == ["ref"]
    assert len(identifiers(api, "ref")) == 1


# ── errors ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("error", [InvalidWeight, InvalidDimensions])
def test_errors_have_common_base(error):
    assert issubclass(error, ClickAndDropError)
    assert issubclass(error, ValueError), "backwards compatible"


def test_strategy_error_codes_differ_from_click_and_drop():
    assert all(code < 0 for code in StrategyErrorCode)


# ── replace_orders: older copies that cannot be deleted ────────────────────────


def test_replace_orders_keeps_manifested_order(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    [old] = identifiers(api, "ref")
    api._orders[old].manifested_on = api.now()
    response = api.replace_orders([make_order("ref"), make_order("other")])
    assert failed(response) == {"ref": StrategyErrorCode.ORDER_MANIFESTED}
    assert created(response) == ["other"]
    assert identifiers(api, "ref") == [old], "the new order is deleted again"
    assert response.success_count == 1
    assert response.errors_count == 1


def test_replace_orders_keeps_printed_order(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    [old] = identifiers(api, "ref")
    label(api, "ref")
    response = api.replace_orders([make_order("ref")])
    assert failed(response) == {"ref": StrategyErrorCode.LABEL_ALREADY_PRINTED}
    assert identifiers(api, "ref") == [old]


def test_replace_orders_deletes_printed_order_if_allowed(api: MockClickAndDrop):
    api.create_order(make_order("ref"))
    [old] = identifiers(api, "ref")
    label(api, "ref")
    response = api.replace_orders([make_order("ref")], delete_printed=True)
    assert created(response) == ["ref"]
    [new] = identifiers(api, "ref")
    assert new != old


def test_replace_orders_without_duplicates_lists_no_orders(api: MockClickAndDrop):
    api.create_orders([make_order(f"old-{i}") for i in range(5)])
    api.page_requests.clear()
    api.replace_orders([make_order("new")])
    assert api.page_requests == []
