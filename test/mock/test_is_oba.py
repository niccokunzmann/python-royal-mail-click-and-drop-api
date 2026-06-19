"""Tests for MockClickAndDrop.is_oba."""

from click_and_drop_api.simple.mock import MockClickAndDrop


def test_is_oba_default_is_true():
    assert MockClickAndDrop().is_oba() is True


def test_is_oba_true():
    assert MockClickAndDrop(is_oba=True).is_oba() is True


def test_is_oba_false():
    assert MockClickAndDrop(is_oba=False).is_oba() is False
