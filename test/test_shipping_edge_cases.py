"""Edge cases of the shipping options and their parsers."""

import pytest

from click_and_drop_api.simple.shipping import get_shipping_options
from click_and_drop_api.simple.shipping.db import ShippingDB
from click_and_drop_api.simple.shipping.oba_parser import parse_oba_file
from click_and_drop_api.simple.shipping.parser import parse_file


@pytest.fixture
def db() -> ShippingDB:
    return ShippingDB.default()


# ── ShippingDB ─────────────────────────────────────────────────────────────────


def test_copy_is_independent(db):
    copy = db.copy()
    assert len(copy) == len(db)
    assert copy is not db


def test_filter_combines_all_filters(db):
    found = db.filter(
        package_size_code="letter",
        service_code="OLP1",
        weight_grams=50,
        is_oba=False,
        international=False,
    )
    assert len(found) > 0
    for option in found:
        assert option.package_size_code == "letter"
        assert option.service_code == "OLP1"
        assert option.weight_can_be_shipped(50)
        assert not option.is_oba
        assert not option.international


def test_filter_without_arguments_keeps_all(db):
    assert len(db.filter()) == len(db)


def test_international_options(db):
    assert {"ITROLP", "TPN24"} & set(db.for_international().service_codes()) == {
        "ITROLP"
    }
    assert all(o.international for o in db.for_international())


def test_package_size_codes(db):
    assert {"letter", "largeLetter", "smallParcel"} <= set(db.package_size_codes())


def test_get_unknown_option_is_none(db):
    assert db.get("letter", "NOT-A-CODE") is None


def test_get_shipping_options_by_code():
    options = get_shipping_options("OLP1", "TPN24")
    assert {o.service_code for o in options} == {"OLP1", "TPN24"}


# ── PackageShippingOption ──────────────────────────────────────────────────────


def test_max_weight_in_kilograms(db):
    option = db.get("letter", "OLP1")
    assert option.max_weight_kg == option.max_weight_g / 1000


def test_dimensions_limited_by_their_sum(db):
    """Some packages limit the sum of the sides, not only each side."""
    option = next(
        o
        for o in db
        if o.max_sum_mm is not None and sum(o.dimensions_mm) > o.max_sum_mm
    )
    assert not option.dimensions_can_be_shipped(*option.dimensions_mm), (
        "each side fits, but the sum is too big"
    )
    assert option.dimensions_can_be_shipped(1, 1, 1)


# ── parsers: incomplete files are skipped ──────────────────────────────────────

INCOMPLETE = {
    # the file ends after the service code
    "end after code": "Service (£20 compensation)\nSee details\n\n\tOLP1 \t\n",
    # no price line after the delivery speed
    "no price line": "Service (£20 compensation)\nSee details\n\tOLP1\n\n24 hour\nsomething else\n",
}


@pytest.mark.parametrize("text", INCOMPLETE.values(), ids=INCOMPLETE.keys())
def test_parse_incomplete_file(tmp_path, text):
    path = tmp_path / "letter-GB.txt"
    path.write_text(text)
    assert parse_file(path, "letter") == []


INCOMPLETE_OBA = {
    "end after code": "Service (01) (£20 compensation)\nSee details\n\n\tBPL1 \t\n",
    "no price line": "Service (01) (£20 compensation)\nSee details\n\tBPL1\n\n24 hour\nsomething else\n",
}


@pytest.mark.parametrize("text", INCOMPLETE_OBA.values(), ids=INCOMPLETE_OBA.keys())
def test_parse_incomplete_oba_file(tmp_path, text):
    path = tmp_path / "letter-GB.txt"
    path.write_text(text)
    assert parse_oba_file(path, "letter") == []
