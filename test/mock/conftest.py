import pytest

from click_and_drop_api.simple.mock import MockClickAndDrop


@pytest.fixture(params=[1, 100])
def api(request: pytest.FixtureRequest) -> MockClickAndDrop:
    api = MockClickAndDrop()
    api.max_order_count = request.param
    return api
