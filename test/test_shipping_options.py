from click_and_drop_api.simple import list_service_codes, check_service_codes
from click_and_drop_api.simple.package_sizes import get_package_size
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
        ("large-letter", ["OLP1", "OLP2", "OLB3"], ["OLP1", "OLP2"]),
        ("small-parcel", ["TOLP24SFA", "TOLP48", "PFEAMSF"], ["TOLP24SFA", "TOLP48"]),
        (
            "medium-parcel",
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
