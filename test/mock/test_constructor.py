"""Tests for MockClickAndDrop constructor."""

import pytest

from click_and_drop_api.simple.mock import MockClickAndDrop


def test_default_key():
    assert MockClickAndDrop().key == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def test_custom_key():
    key = "11111111-2222-3333-4444-555555555555"
    assert MockClickAndDrop(key=key).key == key


def test_invalid_key_type():
    with pytest.raises(TypeError):
        MockClickAndDrop(key=12345)


def test_invalid_key_too_short():
    with pytest.raises(ValueError):
        MockClickAndDrop(key="short")


def test_invalid_key_whitespace():
    with pytest.raises(ValueError):
        MockClickAndDrop(key="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeee ee")
