from click_and_drop_api.simple import list_service_codes, check_service_codes
from click_and_drop_api.simple.package_sizes import PackageSize, get_package_size
from click_and_drop_api.simple.shipping_options import ShippingOption
import pytest


def test_list_all_shipping_options():
    """Test ListAllShippingOptionsResponse"""
    assert list_service_codes()
    assert all(isinstance(code, str) for code in list_service_codes())


def test_check_service_codes():
    """Test CheckServiceCodesResponse"""
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
def test_select_all_shipping_options(package, selected, expected):
    """Test SelectAllShippingOptionsResponse"""
    package = get_package_size(package)
    selected_subset = package.get_shipping_options_in(selected)
    codes = [option.service_code for option in selected_subset]
    assert codes == expected, f"Expected {expected}, got {codes} for {package.code}"
    copy = package.with_shipping_limited_to(selected)
    assert copy.shipping_options == selected_subset
    assert copy.code == package.code
    assert copy.name == package.name
    assert copy.weight_grams == package.weight_grams
    assert copy.length_mm == package.length_mm
    assert copy.width_mm == package.width_mm
    assert copy.height_mm == package.height_mm


def test_shipping_option_conversion_1():
    postage = ShippingOption.with_code("OLP1").as_postage_details()
    assert postage.service_code == "OLP1"
    assert postage.carrier_name == "Royal Mail"


def test_shipping_option_conversion_2():
    postage = ShippingOption.with_code("PFEAMSF").as_postage_details()
    assert postage.service_code == "PFEAMSF"
    assert postage.carrier_name == "Parcel Force"


def test_as_package_request_letter():
    """Check the weight."""
    package = get_package_size("letter")
    assert package.as_package_request(100).weight_in_grams == 100


def test_as_package_request_largeLetter():
    """Check the weight."""
    package = get_package_size("largeLetter")
    assert package.as_package_request(200).weight_in_grams == 200


def test_cannot_be_too_heavy():
    package = get_package_size("letter")
    with pytest.raises(ValueError, match="1g to 100g allowed, got 2000g."):
        package.as_package_request(2000)

    package = get_package_size("largeLetter")
    with pytest.raises(ValueError, match="1g to 1000g allowed, got 3000g."):
        package.as_package_request(3000)


def test_cannot_be_too_big():
    package = get_package_size("letter")
    with pytest.raises(
        ValueError,
        match="1000mm x 1000mm x 1000mm does not fit into 240mm x 165mm x 5mm.",
    ):
        package.as_package_request(100, 1000, 1000, 1000)

    package = get_package_size("largeLetter")
    with pytest.raises(
        ValueError,
        match="1003mm x 1002mm x 1001mm does not fit into 353mm x 250mm x 25mm.",
    ):
        package.as_package_request(1000, 1001, 1003, 1002)


def test_package_request_with_dimensions():
    package = get_package_size("letter")
    package_request = package.as_package_request(100, 3, 34, 4)
    assert package_request.dimensions is not None
    assert package_request.dimensions.height_in_mms == 34
    assert package_request.dimensions.width_in_mms == 4
    assert package_request.dimensions.depth_in_mms == 3


def test_ship_with_low_weight():
    package = get_package_size("letter")
    with pytest.raises(ValueError, match="1g to 100g allowed, got 0g."):
        package.as_package_request(0)


def test_dimensions_order_themselves():
    p = PackageSize("letter", "Letter", 100, 30, 40, 50, [])
    assert p.dimensions_can_be_shipped(30, 40, 50)
    assert p.dimensions_can_be_shipped(30, 50, 40)
    assert p.dimensions_can_be_shipped(50, 30, 40)
    assert p.dimensions_can_be_shipped(50, 40, 30)
    assert p.dimensions_can_be_shipped(40, 30, 50)
    assert p.dimensions_can_be_shipped(40, 50, 30)
    assert not p.dimensions_can_be_shipped(40, 50, 100)
    assert not p.dimensions_can_be_shipped(40, 100, 50)
    assert not p.dimensions_can_be_shipped(100, 40, 50)
    assert not p.dimensions_can_be_shipped(100, 50, 40)


def test_dimensions_order_themselves_2():
    p = PackageSize("letter", "Letter", 100, 401, 301, 501, [])
    assert p.dimensions_can_be_shipped(301, 401, 501)
    assert p.dimensions_can_be_shipped(301, 501, 401)
    assert p.dimensions_can_be_shipped(501, 301, 401)
    assert p.dimensions_can_be_shipped(501, 401, 301)
    assert p.dimensions_can_be_shipped(401, 301, 501)
    assert p.dimensions_can_be_shipped(401, 501, 301)
    assert not p.dimensions_can_be_shipped(401, 501, 1000)
    assert not p.dimensions_can_be_shipped(401, 1000, 501)
    assert not p.dimensions_can_be_shipped(1000, 401, 501)
    assert not p.dimensions_can_be_shipped(1000, 501, 401)


def test_negative_values_not_ok():
    p = PackageSize("letter", "Letter", 100, 401, 301, 501, [])
    assert not p.dimensions_can_be_shipped(-1, 401, 501)
    assert not p.dimensions_can_be_shipped(401, -1, 501)
    assert not p.dimensions_can_be_shipped(401, 501, -1)


def test_dimensions():
    p = PackageSize("letter", "Letter", 100, 401, 301, 501, [])
    assert p.dimensions_mm == (501, 401, 301)
