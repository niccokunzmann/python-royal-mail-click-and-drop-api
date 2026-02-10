from click_and_drop_api.simple import list_service_codes, check_service_codes
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
