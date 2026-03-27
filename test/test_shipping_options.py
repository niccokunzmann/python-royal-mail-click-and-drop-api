import pytest
from click_and_drop_api.simple import check_service_codes, db
from click_and_drop_api.simple.shipping.db import ShippingDB
from click_and_drop_api.simple.shipping.package_shipping_option import (
    PackageShippingOption,
)
from decimal import Decimal as D


def test_list_all_shipping_options():
    codes = db.service_codes()
    assert codes
    assert all(isinstance(code, str) for code in codes)


def test_check_service_codes():
    check_service_codes(["OLP1", "OLP2"])
    with pytest.raises(ValueError):
        check_service_codes(["OLP1", "OLP2", "OLB3"])


@pytest.mark.parametrize(
    ("package", "selected", "expected"),
    [
        ("letter", ["OLP1", "OLP2"], ["OLP1", "OLP2"]),
        ("largeLetter", ["OLP1", "OLP2", "OLB3"], ["OLP1", "OLP2"]),
        ("smallParcel", ["TOLP24SFA", "TOLP48", "PFEAMSF"], ["TOLP24SFA", "TOLP48"]),
        (
            "mediumParcel",
            ["TOLP24SFA", "TOLP48", "PFEAMSF"],
            ["TOLP24SFA", "TOLP48", "PFEAMSF"],
        ),
    ],
)
def test_select_shipping_options(package, selected, expected):
    selected_set = set(selected)
    options = [
        o for o in db.for_package_size(package) if o.service_code in selected_set
    ]
    codes = {o.service_code for o in options}
    assert codes == set(expected)


def test_shipping_option_conversion_1():
    postage = db.get("letter", "OLP1").as_postage_details()
    assert postage.service_code == "OLP1"


def test_shipping_option_conversion_2():
    postage = db.get("largeParcel", "PFEAMSF").as_postage_details()
    assert postage.service_code == "PFEAMSF"


def test_as_package_request_letter():
    option = db.get("letter", "OLP1")
    assert option.as_package_request(100).weight_in_grams == 100


def test_as_package_request_large_letter():
    option = db.get("largeLetter", "OLP1")
    assert option.as_package_request(200).weight_in_grams == 200


def test_cannot_be_too_heavy():
    option = db.get("letter", "OLP1")
    with pytest.raises(ValueError, match="1g to 100g allowed"):
        option.as_package_request(2000)

    option = db.get("largeLetter", "OLP1")
    with pytest.raises(ValueError, match="1g to 1000g allowed"):
        option.as_package_request(3000)


def test_cannot_be_too_big():
    option = db.get("letter", "OLP1")
    with pytest.raises(ValueError, match="does not fit into"):
        option.as_package_request(100, 1000, 1000, 1000)

    option = db.get("largeLetter", "OLP1")
    with pytest.raises(ValueError, match="does not fit into"):
        option.as_package_request(1000, 1001, 1003, 1002)


def test_package_request_with_dimensions():
    option = db.get("letter", "OLP1")
    package_request = option.as_package_request(100, 3, 34, 4)
    assert package_request.dimensions is not None
    assert package_request.dimensions.height_in_mms == 34
    assert package_request.dimensions.width_in_mms == 4
    assert package_request.dimensions.depth_in_mms == 3


def test_ship_with_low_weight():
    options = db.for_package_size("letter").for_service("OLP1")
    with pytest.raises(ValueError, match="1g to 100g allowed, got 0g."):
        options[0].as_package_request(0)


@pytest.mark.parametrize(
    "dims,fits",
    [
        ((30, 40, 50), True),
        ((30, 50, 40), True),
        ((50, 30, 40), True),
        ((50, 40, 30), True),
        ((40, 30, 50), True),
        ((40, 50, 30), True),
        ((40, 50, 100), False),
        ((40, 100, 50), False),
        ((100, 40, 50), False),
        ((100, 50, 40), False),
    ],
)
def test_dimensions_order_themselves(dims, fits):
    p = PackageShippingOption(
        package_size_code="letter",
        package_name="Letter",
        package_max_weight_g=100,
        depth_mm=30,
        width_mm=40,
        height_mm=50,
        brand="",
        service="",
        service_code="",
        delivery_speed="",
        compensation=D("0"),
        gross=D("0"),
    )
    assert p.dimensions_can_be_shipped(*dims) is fits


def test_dimensions():
    p = PackageShippingOption(
        package_size_code="letter",
        package_name="Letter",
        package_max_weight_g=100,
        depth_mm=401,
        width_mm=301,
        height_mm=501,
        brand="",
        service="",
        service_code="",
        delivery_speed="",
        compensation=D("0"),
        gross=D("0"),
    )
    assert p.dimensions_mm == (501, 401, 301)


def test_negative_values_not_ok():
    p = PackageShippingOption(
        package_size_code="letter",
        package_name="Letter",
        package_max_weight_g=100,
        depth_mm=401,
        width_mm=301,
        height_mm=501,
        brand="",
        service="",
        service_code="",
        delivery_speed="",
        compensation=D("0"),
        gross=D("0"),
    )
    assert not p.dimensions_can_be_shipped(-1, 401, 501)
    assert not p.dimensions_can_be_shipped(401, -1, 501)
    assert not p.dimensions_can_be_shipped(401, 501, -1)


def test_db_len():
    assert len(db) > 0


def test_db_bool():
    assert db
    assert not ShippingDB([])


def test_db_iter():
    options = list(db)
    assert len(options) == len(db)
    assert all(hasattr(o, "service_code") for o in options)


def test_db_getitem():
    first = db[0]
    assert hasattr(first, "service_code")


def test_db_any():
    assert db.any is db[0]


def test_db_any_raises_on_empty():
    with pytest.raises(IndexError):
        ShippingDB([]).any


def test_db_any_or_none_non_empty():
    assert db.any_or_none is db[0]


def test_db_any_or_none_empty():
    assert ShippingDB([]).any_or_none is None


def test_db_str():
    for option in db:
        assert repr(option.package_size_code) in repr(db)
        assert repr(option.service_code) in repr(db)

    assert db.__class__.__name__ in repr(db)
