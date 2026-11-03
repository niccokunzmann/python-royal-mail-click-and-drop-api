"""Run the integration tests against the mock and against the real Click & Drop API.

The real API is only used if the environment variables ``CI=true`` and ``API_KEY`` are set.
All orders created by a test are deleted after the test.
"""

import os
import time
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone

import pytest
from click_and_drop_api.exceptions import ServiceException

from click_and_drop_api.simple import (
    Address,
    ClickAndDrop,
    CreateOrder,
    MockClickAndDrop,
    NullStrategy,
    RecipientDetails,
)

REAL_API = os.environ.get("CI") == "true" and bool(os.environ.get("API_KEY"))


class Throttle:
    """Stay below the rate limit of 5 calls per second."""

    DELAY = 0.3

    def __init__(self):
        self.last = 0.0

    def wait(self):
        pause = self.last + self.DELAY - time.monotonic()
        if pause > 0:
            time.sleep(pause)
        self.last = time.monotonic()


class RecordingMixin:
    """Remember the created orders to delete them after the test, and count the requests.

    Click & Drop sometimes answers with "500 Internal Server Error".
    Requests that can be repeated are tried again and counted once.
    Creating orders is not repeated: the orders might have been created.
    """

    RETRIES = 3

    def _create_orders(self, orders):
        self._request("create")
        response = super()._create_orders(orders)
        self.created_identifiers.extend(
            o.order_identifier for o in response.created_orders
        )
        return response

    def _get_orders(self, order_identifiers):
        return self._repeatable("get", super()._get_orders, order_identifiers)

    def _get_orders_page(self, *args):
        return self._repeatable("page", super()._get_orders_page, *args)

    def _delete_orders(self, order_identifiers):
        return self._repeatable("delete", super()._delete_orders, order_identifiers)

    def _request(self, kind: str):
        self._throttle()
        self.requests[kind] += 1

    def _repeatable(self, kind: str, request, *args):
        self.requests[kind] += 1
        for attempt in range(self.RETRIES):
            self._throttle()
            try:
                return request(*args)
            except ServiceException:
                if attempt == self.RETRIES - 1:
                    raise
                time.sleep(2**attempt)


class RealAPI(RecordingMixin, ClickAndDrop):
    def __init__(self, key):
        super().__init__(key)
        self.created_identifiers = []
        self.requests = Counter()
        self._throttle = Throttle().wait


class MockAPI(RecordingMixin, MockClickAndDrop):
    """Configured like the account of the real API: OLP, not OBA, not ChannelShipper."""

    def __init__(self):
        super().__init__(is_oba=False, channel_shipper=False)
        self.created_identifiers = []
        self.requests = Counter()
        self._throttle = lambda: None


LEFTOVER_AGE = timedelta(hours=1)
"""Test orders older than this are left over from interrupted test runs.

Younger ones may belong to a test run at the same time.
"""


@pytest.fixture(scope="session", autouse=True)
def remove_leftover_test_orders():
    """Delete the orders of interrupted test runs before the tests start.

    Each test run uses new references, so leftovers cannot cause duplicates.
    """
    if not REAL_API:
        return
    api = RealAPI(os.environ["API_KEY"])
    cutoff = (api.now() - LEFTOVER_AGE).replace(tzinfo=None)
    leftovers = [
        o.order_identifier
        for o in api.iter_orders()
        if (o.order_reference or "").startswith("test")
        and o.created_on.replace(tzinfo=None) < cutoff
        and o.manifested_on is None
    ]
    if leftovers:
        api.delete_orders(leftovers)


@pytest.fixture(
    params=[
        "mock",
        pytest.param(
            "real",
            marks=pytest.mark.skipif(
                not REAL_API, reason="Set CI=true and API_KEY to test the real API."
            ),
        ),
    ]
)
def api(request):
    api = RealAPI(os.environ["API_KEY"]) if request.param == "real" else MockAPI()
    started = api.now() - timedelta(seconds=5)
    yield api
    created = set(api.created_identifiers)
    if not created:
        return
    remaining = [o.order_identifier for o in api.iter_recent_orders(until=started)]
    to_delete = sorted(created & set(remaining))
    if to_delete:
        api.delete_orders(to_delete)
    left = created & {o.order_identifier for o in api.iter_recent_orders(until=started)}
    assert not left, f"cleanup failed, delete these orders: {sorted(left)}"


@pytest.fixture
def reference():
    """A new order reference for each call.  All of them start with "test"."""
    run = uuid.uuid4().hex[:8]
    counter = iter(range(1000))
    return lambda: f"test-{run}-{next(counter)}"


def order(reference: str) -> CreateOrder:
    """A minimal order that is not sent anywhere."""
    assert reference.startswith("test"), "uploaded references must start with test"
    return CreateOrder(
        order_reference=reference,
        order_date=datetime.now(timezone.utc),
        subtotal=1.00,
        shipping_cost_charged=0.00,
        total=1.00,
        currency_code="GBP",
        recipient=RecipientDetails(
            address=Address(
                full_name="Integration Test",
                address_line1="1 Test Street",
                city="London",
                postcode="SW1A 1AA",
                country_code="GB",
            )
        ),
    )


@pytest.fixture
def create(api):
    """Upload orders, each in its own request, and wait until Click & Drop finds them.

    Several orders with the same reference create duplicates,
    like a checkout that is retried.

    Returns:
        The identifiers of the created orders.
    """

    def create(*references: str, timeout: float = 30) -> list[int]:
        started = api.now() - timedelta(seconds=5)
        identifiers = []
        for ref in references:
            response = api.create_orders([order(ref)], strategy=NullStrategy())
            assert not response.failed_orders, response.failed_orders
            identifiers.extend(o.order_identifier for o in response.created_orders)
        counts = Counter(references)
        deadline = time.monotonic() + timeout
        while True:
            listed = {o.order_identifier for o in api.iter_recent_orders(until=started)}
            lookup = api.lookup_references(list(counts))
            if set(identifiers) <= listed and all(
                ref in (lookup.unique if count == 1 else lookup.ambiguous)
                for ref, count in counts.items()
            ):
                return identifiers
            assert time.monotonic() < deadline, f"orders not reachable: {references}"
            time.sleep(0.5)

    return create
