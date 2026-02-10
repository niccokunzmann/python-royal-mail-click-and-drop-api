from click_and_drop_api.simple import ClickAndDrop
import pytest


def test_type_error_malformed_input():
    """We get wrong types."""
    with pytest.raises(TypeError):
        ClickAndDrop(None)
    with pytest.raises(TypeError):
        ClickAndDrop([])


def test_value_error_on_malformed_key():
    """We get bad values."""
    with pytest.raises(ValueError):
        ClickAndDrop("")

    with pytest.raises(ValueError):
        ClickAndDrop("test 123")

    with pytest.raises(ValueError):
        ClickAndDrop("aaaaaaaa-bbbb-cccc-dddd-eee eeeeeee")


def test_valid_formatted_key():
    """We get good values."""
    api = ClickAndDrop("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    assert api.key == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def test_valid_key_with_whitespace():
    api = ClickAndDrop("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n")
    assert api.key == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
