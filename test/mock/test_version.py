"""Tests for MockClickAndDrop.get_version."""

from datetime import datetime

from click_and_drop_api.simple.mock import MockClickAndDrop


def test_get_version_returns_mock_release(api: MockClickAndDrop):
    version = api.get_version()
    assert version.release == "1.0.0-mock"
    assert version.commit == "mock"
    assert version.build == "mock"
    assert isinstance(version.release_date, datetime)
