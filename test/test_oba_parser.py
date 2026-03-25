"""Tests for the OBA parser and OBA shipping option modules."""

from click_and_drop_api.simple.shipping.parcel import options as parcel_options
from click_and_drop_api.simple.shipping.documents import (
    options as documents_options,
)
from click_and_drop_api.simple.shipping.large_letter import (
    options as large_letter_options,
)
from click_and_drop_api.simple.shipping.letter import options as letter_options


def _oba(options):
    return [o for o in options if o.is_oba]


def test_letter_contains_oba_options():
    assert any(o.is_oba for o in letter_options)


def test_large_letter_oba_max_weight():
    assert all(o.max_weight_g == 750 for o in _oba(large_letter_options))


def test_parcel_oba_max_weight():
    assert all(o.max_weight_g == 30_000 for o in parcel_options)


def test_parcel_is_oba():
    assert all(o.is_oba for o in parcel_options)


def test_documents_international():
    assert all(o.international for o in documents_options)


def test_oba_brand():
    assert all(o.brand == "Royal Mail OBA" for o in _oba(letter_options))


def test_oba_signed_for_parsed():
    signed = [o for o in _oba(letter_options) if o.signed_for]
    assert len(signed) > 0


def test_oba_local_collect_parsed():
    local = [o for o in parcel_options if o.local_collect]
    assert len(local) > 0


def test_oba_ioss_international():
    ioss = [o for o in documents_options if o.ioss]
    assert len(ioss) > 0


def test_non_oba_options_not_flagged():
    non_oba = [o for o in letter_options if not o.is_oba]
    assert len(non_oba) > 0
    print([o.max_weight_g for o in non_oba])
    assert all(o.max_weight_g == 100 for o in non_oba)
