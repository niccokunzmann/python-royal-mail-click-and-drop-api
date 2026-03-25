"""Tests for OBA parcel per-service-code physical constraints (weight + dimensions).

Royal Mail OBA services:
  - No single side > 60 cm (600 mm)
  - L + W + D ≤ 90 cm (900 mm)
  - Weight limit varies per service code (2 kg / 10 kg / 20 kg)

Parcel Force services (FE0–FE3, NDA–NDE):
  - Longest side ≤ 150 cm (1500 mm)
  - L + W + D ≤ 300 cm (3000 mm)
  - Max weight 30 kg
"""

import pytest

from click_and_drop_api.simple.shipping.parcel import (
    SERVICE_CONSTRAINTS,
)

# ---------------------------------------------------------------------------
# Representative codes for each category
# ---------------------------------------------------------------------------
_RM_2KG_CODES = [
    "BPL1",
    "BPL2",
    "BPR1",
    "BPR2",
    "STL1",
    "STL2",
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
]
_RM_10KG_CODES = ["SDV", "SDW", "SDX", "SDY", "SDZ", "SEA", "SEB", "SEC", "SED"]
_RM_20KG_CODES = ["TPN24", "TPS48", "TRN24", "TRS48"]
_PF_CODES = ["FE0", "FE1", "FE2", "FE3", "NDA", "NDB", "NDC", "NDE"]
_ALL_RM_CODES = _RM_2KG_CODES + _RM_10KG_CODES + _RM_20KG_CODES


# ---------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------


def test_all_codes_have_constraints():
    from click_and_drop_api.simple.shipping.parcel import SERVICE_MAX_WEIGHT_G

    assert set(SERVICE_CONSTRAINTS) == set(SERVICE_MAX_WEIGHT_G)


@pytest.mark.parametrize("code", _ALL_RM_CODES)
def test_rm_has_max_single_side(code):
    c = SERVICE_CONSTRAINTS[code]
    assert c.max_single_side_mm == 600
    assert c.max_combined_mm == 900
    assert c.max_length_mm is None


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_has_max_length(code):
    c = SERVICE_CONSTRAINTS[code]
    assert c.max_length_mm == 1_500
    assert c.max_combined_mm == 3_000
    assert c.max_single_side_mm is None


# ---------------------------------------------------------------------------
# Royal Mail OBA — weight limits
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", _RM_2KG_CODES)
def test_rm_2kg_max_weight(code):
    assert SERVICE_CONSTRAINTS[code].max_weight_g == 2_000


@pytest.mark.parametrize("code", _RM_10KG_CODES)
def test_rm_10kg_max_weight(code):
    assert SERVICE_CONSTRAINTS[code].max_weight_g == 10_000


@pytest.mark.parametrize("code", _RM_20KG_CODES)
def test_rm_20kg_max_weight(code):
    assert SERVICE_CONSTRAINTS[code].max_weight_g == 20_000


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_30kg_max_weight(code):
    assert SERVICE_CONSTRAINTS[code].max_weight_g == 30_000


# ---------------------------------------------------------------------------
# Royal Mail OBA — fits() dimension checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", _ALL_RM_CODES)
def test_rm_fits_within_limits(code):
    # 300 × 300 × 300 mm: combined = 900, max side = 300 — should pass
    assert SERVICE_CONSTRAINTS[code].fits(1_000, 300, 300, 300)


@pytest.mark.parametrize("code", _ALL_RM_CODES)
def test_rm_rejects_side_over_600mm(code):
    # 610 × 140 × 150 mm: combined = 900, but one side = 610 > 600
    assert not SERVICE_CONSTRAINTS[code].fits(1_000, 610, 140, 150)


@pytest.mark.parametrize("code", _ALL_RM_CODES)
def test_rm_rejects_combined_over_900mm(code):
    # 400 × 300 × 201 mm: combined = 901 > 900
    assert not SERVICE_CONSTRAINTS[code].fits(1_000, 400, 300, 201)


@pytest.mark.parametrize("code", _ALL_RM_CODES)
def test_rm_accepts_combined_exactly_900mm(code):
    # 400 × 300 × 200 mm: combined = 900, max side = 400 ≤ 600
    assert SERVICE_CONSTRAINTS[code].fits(1_000, 400, 300, 200)


@pytest.mark.parametrize("code", _RM_2KG_CODES)
def test_rm_2kg_rejects_overweight(code):
    assert not SERVICE_CONSTRAINTS[code].fits(2_001, 300, 300, 300)


@pytest.mark.parametrize("code", _RM_2KG_CODES)
def test_rm_2kg_accepts_at_limit(code):
    assert SERVICE_CONSTRAINTS[code].fits(2_000, 300, 300, 300)


# ---------------------------------------------------------------------------
# Parcel Force — fits() dimension checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_fits_within_limits(code):
    # 1000 × 1000 × 1000 mm: combined = 3000, max side = 1000 ≤ 1500
    assert SERVICE_CONSTRAINTS[code].fits(10_000, 1_000, 1_000, 1_000)


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_rejects_length_over_1500mm(code):
    # 1501 × 100 × 100 mm
    assert not SERVICE_CONSTRAINTS[code].fits(1_000, 1_501, 100, 100)


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_accepts_length_exactly_1500mm(code):
    # 1500 × 100 × 100 mm: combined = 1700, max side = 1500
    assert SERVICE_CONSTRAINTS[code].fits(1_000, 1_500, 100, 100)


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_rejects_combined_over_3000mm(code):
    # 1000 × 1000 × 1001 mm: combined = 3001
    assert not SERVICE_CONSTRAINTS[code].fits(1_000, 1_000, 1_000, 1_001)


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_accepts_combined_exactly_3000mm(code):
    assert SERVICE_CONSTRAINTS[code].fits(1_000, 1_000, 1_000, 1_000)


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_rejects_overweight(code):
    assert not SERVICE_CONSTRAINTS[code].fits(30_001, 500, 500, 500)


@pytest.mark.parametrize("code", _PF_CODES)
def test_pf_accepts_at_weight_limit(code):
    assert SERVICE_CONSTRAINTS[code].fits(30_000, 500, 500, 500)


# ---------------------------------------------------------------------------
# ServiceConstraint.fits() is dimension-order-independent
# ---------------------------------------------------------------------------


def test_fits_dimension_order_independent():
    c = SERVICE_CONSTRAINTS["BPL1"]
    assert c.fits(1_000, 400, 300, 200) == c.fits(1_000, 200, 400, 300)
    assert c.fits(1_000, 200, 400, 300) == c.fits(1_000, 300, 200, 400)
