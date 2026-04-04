# non-OBA
# status: new
# Order identifier : 2684
# Order reference  : None
# Created on       : 2026-04-04 15:51:22.230521
# Order date       : 2026-04-04 15:51:22.196067
# Printed on       : None
# Manifested on    : None
# Shipped on       : None
# Tracking number  : None
# Packages (1):

# status: postage applied
# Order identifier : 2179
# Order reference  : example-order-20260325104224
# Created on       : 2026-03-25 10:42:24.668141
# Order date       : 2026-03-25 10:42:24.197209
# Printed on       : None
# Manifested on    : None
# Shipped on       : None
# Tracking number  : None
# Packages (1):
#   #1  tracking: None

# status: Label Generated
# Order identifier : 1027
# Order reference  : example-order-20260214203002
# Created on       : 2026-02-14 20:30:02.527104
# Order date       : 2026-02-14 20:30:02.305390
# Printed on       : 2026-02-14 20:48:22.379152
# Manifested on    : None
# Shipped on       : None
# Tracking number  : None
# Packages (1):
#   #1  tracking: None

# status: Manifested
# Order identifier : 1318
# Order reference  : oba-workflow-20260404140306
# Created on       : 2026-04-04 14:03:06.489139
# Order date       : 2026-04-04 14:03:06.410889
# Printed on       : 2026-04-04 14:03:06.914848
# Manifested on    : 2026-04-04 14:03:09.954994
# Shipped on       : 2026-04-04 14:03:09.954994
# Tracking number  : None
# Packages (1):
#   #1  tracking: None

from datetime import datetime, timezone

from click_and_drop_api.models.get_order_info_resource import GetOrderInfoResource
from click_and_drop_api.simple.types import OrderInfo

S = OrderInfo.STATUS

_T1 = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
_T2 = datetime(2026, 4, 4, 13, 0, 0, tzinfo=timezone.utc)
_T3 = datetime(2026, 4, 4, 14, 0, 0, tzinfo=timezone.utc)
_T4 = datetime(2026, 4, 4, 15, 0, 0, tzinfo=timezone.utc)


def _make(
    created_on=_T1,
    printed_on=None,
    manifested_on=None,
    shipped_on=None,
) -> OrderInfo:
    return OrderInfo(
        order_identifier=1,
        created_on=created_on,
        printed_on=printed_on,
        manifested_on=manifested_on,
        shipped_on=shipped_on,
    )


def test_history_only_new_when_no_timestamps():
    assert _make().status_history == [S.NEW]


def test_history_new_then_label_generated():
    assert _make(printed_on=_T2).status_history == [S.NEW, S.LABEL_GENERATED]


def test_history_new_then_manifested():
    assert _make(manifested_on=_T2).status_history == [S.NEW, S.MANIFESTED]


def test_history_new_then_despatched():
    assert _make(shipped_on=_T2).status_history == [S.NEW, S.DESPATCHED]


def test_history_full_normal_order():
    order = _make(printed_on=_T2, manifested_on=_T3, shipped_on=_T4)
    assert order.status_history == [
        S.NEW,
        S.LABEL_GENERATED,
        S.MANIFESTED,
        S.DESPATCHED,
    ]


def test_history_order_when_shipped_before_manifested():
    # unusual data: shipped_on < manifested_on — history must follow timestamps
    order = _make(printed_on=_T2, shipped_on=_T3, manifested_on=_T4)
    assert order.status_history == [
        S.NEW,
        S.LABEL_GENERATED,
        S.DESPATCHED,
        S.MANIFESTED,
    ]


def test_history_order_when_manifested_before_printed():
    # unusual data: manifested_on < printed_on
    order = _make(manifested_on=_T2, printed_on=_T3)
    assert order.status_history == [S.NEW, S.MANIFESTED, S.LABEL_GENERATED]


def test_history_new_always_first():
    order = _make(printed_on=_T2, manifested_on=_T3, shipped_on=_T4)
    assert order.status_history[0] == S.NEW


def test_history_last_entry_is_current_status_new():
    assert _make().status_history[-1] == S.NEW


def test_history_last_entry_is_current_status_label_generated():
    assert _make(printed_on=_T2).status_history[-1] == S.LABEL_GENERATED


def test_history_last_entry_is_current_status_manifested():
    assert _make(printed_on=_T2, manifested_on=_T3).status_history[-1] == S.MANIFESTED


def test_history_last_entry_is_current_status_despatched():
    assert (
        _make(printed_on=_T2, manifested_on=_T3, shipped_on=_T4).status_history[-1]
        == S.DESPATCHED
    )


# --- from_get_order_info_resource ---


def _make_resource(**kwargs) -> GetOrderInfoResource:
    return GetOrderInfoResource(order_identifier=42, created_on=_T1, **kwargs)


def test_from_resource_returns_order_info():
    resource = _make_resource()
    order = OrderInfo.from_get_order_info_resource(resource)
    assert isinstance(order, OrderInfo)


def test_from_resource_preserves_identifier():
    order = OrderInfo.from_get_order_info_resource(_make_resource())
    assert order.order_identifier == 42


def test_from_resource_preserves_created_on():
    order = OrderInfo.from_get_order_info_resource(_make_resource())
    assert order.created_on == _T1


def test_from_resource_preserves_order_reference():
    resource = _make_resource(order_reference="my-ref")
    order = OrderInfo.from_get_order_info_resource(resource)
    assert order.order_reference == "my-ref"


def test_from_resource_preserves_printed_on():
    resource = _make_resource(printed_on=_T2)
    order = OrderInfo.from_get_order_info_resource(resource)
    assert order.printed_on == _T2


def test_from_resource_preserves_manifested_on():
    resource = _make_resource(manifested_on=_T3)
    order = OrderInfo.from_get_order_info_resource(resource)
    assert order.manifested_on == _T3


def test_from_resource_preserves_shipped_on():
    resource = _make_resource(shipped_on=_T4)
    order = OrderInfo.from_get_order_info_resource(resource)
    assert order.shipped_on == _T4


def test_from_resource_status_history_reflects_fields():
    resource = _make_resource(printed_on=_T2, manifested_on=_T3)
    order = OrderInfo.from_get_order_info_resource(resource)
    assert order.status_history == [S.NEW, S.LABEL_GENERATED, S.MANIFESTED]
