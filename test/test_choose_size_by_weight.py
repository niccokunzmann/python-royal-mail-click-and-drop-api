from click_and_drop_api.simple import choose_package_size_by_weight

import pytest


@pytest.mark.parametrize(
    "weight_grams, expected_package_size",
    [
        (0, "letter"),
        (100, "letter"),
        (101, "largeLetter"),
        (1000, "largeLetter"),
        (1001, "smallParcel"),
        (2000, "smallParcel"),
        (2001, "mediumParcel"),
        (20000, "mediumParcel"),
        (20001, "largeParcel"),
        (30000, "largeParcel"),
    ],
)
def test_choose_size_by_weight(weight_grams, expected_package_size):
    package_size = choose_package_size_by_weight(weight_grams)
    assert package_size.code == expected_package_size


@pytest.mark.parametrize(
    "weight_grams, expected_package_size",
    [
        (0, "largeLetter"),
        (100, "largeLetter"),
        (101, "largeLetter"),
        (1000, "largeLetter"),
        (1001, "smallParcel"),
        (2000, "smallParcel"),
    ],
)
def test_choose_size_by_weight_limited(weight_grams, expected_package_size):
    package_size = choose_package_size_by_weight(
        weight_grams, ["largeLetter", "smallParcel"]
    )
    assert package_size.code == expected_package_size


def test_too_much_weight():
    assert choose_package_size_by_weight(3000001) is None
    assert choose_package_size_by_weight(2001, ["largeLetter", "smallParcel"]) is None
