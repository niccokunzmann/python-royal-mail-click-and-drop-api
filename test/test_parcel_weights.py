"""Tests for OBA parcel per-service-code weight limits (SERVICE_MAX_WEIGHT_G).

The limits were verified against the live API using scripts/test_parcel_orders.py.
"""

import pytest

from click_and_drop_api.simple.shipping.parcel import SERVICE_MAX_WEIGHT_G

_3KG = 3_000

# Service codes whose limit allows 3 kg  (limit >= 3,000 g)
_ALLOWS_3KG = [
    # Parcel Force express48 — 30 kg
    ("FE0", 30_000),
    ("FE1", 30_000),
    ("FE2", 30_000),
    ("FE3", 30_000),
    # Parcel Force express24 — 30 kg
    ("NDA", 30_000),
    ("NDB", 30_000),
    ("NDC", 30_000),
    ("NDE", 30_000),
    # Tracked 24 / 48 — 20 kg
    ("TPN24", 20_000),
    ("TPS48", 20_000),
    ("TRN24", 20_000),
    ("TRS48", 20_000),
    # Special Delivery Guaranteed (end-of-day) — 10 kg
    ("SDV", 10_000),
    ("SDW", 10_000),
    ("SDX", 10_000),
    ("SDY", 10_000),
    ("SDZ", 10_000),
    ("SEA", 10_000),
    ("SEB", 10_000),
    ("SEC", 10_000),
    ("SED", 10_000),
]

# Service codes whose limit rejects 3 kg  (limit < 3,000 g)
_REJECTS_3KG = [
    # 1st / 2nd Class + Signed For — 2 kg
    ("BPL1", 2_000),
    ("BPL2", 2_000),
    ("BPR1", 2_000),
    ("BPR2", 2_000),
    # Special Delivery by time — 2 kg
    ("SD1", 2_000),
    ("SD2", 2_000),
    ("SD3", 2_000),
    ("SD4", 2_000),
    ("SD5", 2_000),
    ("SD6", 2_000),
    ("SDA", 2_000),
    ("SDB", 2_000),
    ("SDC", 2_000),
    ("SDE", 2_000),
    ("SDF", 2_000),
    ("SDG", 2_000),
    ("SDH", 2_000),
    ("SDJ", 2_000),
    ("SDK", 2_000),
    ("SDM", 2_000),
    ("SDN", 2_000),
    ("SDQ", 2_000),
    # Account Mail — 2 kg
    ("STL1", 2_000),
    ("STL2", 2_000),
]

_11KG = 11_000
_21KG = 21_000

# 11 kg: only 20 kg and 30 kg codes allow it; 2 kg and 10 kg codes reject it
_ALLOWS_11KG = [
    "FE0",
    "FE1",
    "FE2",
    "FE3",
    "NDA",
    "NDB",
    "NDC",
    "NDE",
    "TPN24",
    "TPS48",
    "TRN24",
    "TRS48",
]
_REJECTS_11KG = [
    "BPL1",
    "BPL2",
    "BPR1",
    "BPR2",
    "SD1",
    "SD2",
    "SD3",
    "SD4",
    "SD5",
    "SD6",
    "SDA",
    "SDB",
    "SDC",
    "SDE",
    "SDF",
    "SDG",
    "SDH",
    "SDJ",
    "SDK",
    "SDM",
    "SDN",
    "SDQ",
    "SDV",
    "SDW",
    "SDX",
    "SDY",
    "SDZ",
    "SEA",
    "SEB",
    "SEC",
    "SED",
    "STL1",
    "STL2",
]

# 21 kg: only 30 kg codes allow it; everything else rejects it
_ALLOWS_21KG = [
    "FE0",
    "FE1",
    "FE2",
    "FE3",
    "NDA",
    "NDB",
    "NDC",
    "NDE",
]
_REJECTS_21KG = [
    "BPL1",
    "BPL2",
    "BPR1",
    "BPR2",
    "SD1",
    "SD2",
    "SD3",
    "SD4",
    "SD5",
    "SD6",
    "SDA",
    "SDB",
    "SDC",
    "SDE",
    "SDF",
    "SDG",
    "SDH",
    "SDJ",
    "SDK",
    "SDM",
    "SDN",
    "SDQ",
    "SDV",
    "SDW",
    "SDX",
    "SDY",
    "SDZ",
    "SEA",
    "SEB",
    "SEC",
    "SED",
    "STL1",
    "STL2",
    "TPN24",
    "TPS48",
    "TRN24",
    "TRS48",
]


@pytest.mark.parametrize("code,expected_limit", _ALLOWS_3KG)
def test_allows_3kg(code, expected_limit):
    assert SERVICE_MAX_WEIGHT_G[code] == expected_limit
    assert SERVICE_MAX_WEIGHT_G[code] >= _3KG


@pytest.mark.parametrize("code,expected_limit", _REJECTS_3KG)
def test_rejects_3kg(code, expected_limit):
    assert SERVICE_MAX_WEIGHT_G[code] == expected_limit
    assert SERVICE_MAX_WEIGHT_G[code] < _3KG


@pytest.mark.parametrize("code", _ALLOWS_11KG)
def test_allows_11kg(code):
    assert SERVICE_MAX_WEIGHT_G[code] >= _11KG


@pytest.mark.parametrize("code", _REJECTS_11KG)
def test_rejects_11kg(code):
    assert SERVICE_MAX_WEIGHT_G[code] < _11KG


@pytest.mark.parametrize("code", _ALLOWS_21KG)
def test_allows_21kg(code):
    assert SERVICE_MAX_WEIGHT_G[code] >= _21KG


@pytest.mark.parametrize("code", _REJECTS_21KG)
def test_rejects_21kg(code):
    assert SERVICE_MAX_WEIGHT_G[code] < _21KG


def test_total_known_codes():
    # 21 codes allow 3 kg (10 kg / 20 kg / 30 kg), 24 reject it (2 kg)
    assert len(SERVICE_MAX_WEIGHT_G) == len(_ALLOWS_3KG) + len(_REJECTS_3KG) == 45


def test_all_allows_3kg_codes_present():
    for code, _ in _ALLOWS_3KG:
        assert code in SERVICE_MAX_WEIGHT_G


def test_all_rejects_3kg_codes_present():
    for code, _ in _REJECTS_3KG:
        assert code in SERVICE_MAX_WEIGHT_G
