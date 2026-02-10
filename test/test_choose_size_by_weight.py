from click_and_drop_api.simple import choose_package_size_by_weight

import pytest


@pytest.mark.parametrize(
    "weight_grams, expected_package_size",
    [
        (0, "letter"),
        (100, "letter"),
        (101, "large-letter"),
        (1000, "large-letter"),
        (1001, "small-parcel"),
        (2000, "small-parcel"),
        (2001, "medium-parcel"),
        (20000, "medium-parcel"),
        (20001, "large-parcel"),
        (30000, "large-parcel"),
    ],
)
def test_choose_size_by_weight(weight_grams, expected_package_size):
    package_size = choose_package_size_by_weight(weight_grams)
    assert package_size.code == expected_package_size


def test_too_much_weight():
    assert choose_package_size_by_weight(3000001) is None
