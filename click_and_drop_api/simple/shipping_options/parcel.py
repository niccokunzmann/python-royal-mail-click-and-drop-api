"""Shipping options for OBA parcels."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .oba_parser import parse_oba_file


@dataclass(frozen=True)
class ServiceConstraint:
    """Physical limits for a single OBA parcel service code.

    Attributes:
        max_weight_g: Maximum weight in grams.
        max_combined_mm: Maximum sum of length + width + depth in mm.
        max_single_side_mm: No individual side may exceed this (Royal Mail services).
        max_length_mm: Longest side must not exceed this (Parcel Force services).
    """

    max_weight_g: int
    max_combined_mm: int
    max_single_side_mm: Optional[int] = None
    max_length_mm: Optional[int] = None

    def fits(
        self,
        weight_g: int,
        length_mm: int,
        width_mm: int,
        depth_mm: int,
    ) -> bool:
        """Return True if the parcel is within all limits for this service."""
        if weight_g > self.max_weight_g:
            return False
        dims = sorted([length_mm, width_mm, depth_mm], reverse=True)
        if sum(dims) > self.max_combined_mm:
            return False
        if self.max_single_side_mm is not None and dims[0] > self.max_single_side_mm:
            return False
        if self.max_length_mm is not None and dims[0] > self.max_length_mm:
            return False
        return True


_dir = Path(__file__).parent

options = [
    *parse_oba_file(
        _dir / "oba-codes" / "parcel-GB.txt", "parcel", max_weight_g=30_000
    ),
    *parse_oba_file(
        _dir / "oba-codes" / "parcel-DE.txt", "parcel", max_weight_g=30_000
    ),
]

# Per-service-code maximum weight limits in grams.
# These were verified by running scripts/test_parcel_orders.py against the live API.
# Codes not listed here have unknown limits.
SERVICE_MAX_WEIGHT_G: dict[str, int] = {
    # 1st / 2nd Class
    "BPL1": 2_000,
    "BPL2": 2_000,
    # Signed For
    "BPR1": 2_000,
    "BPR2": 2_000,
    # Parcel Force express48
    "FE0": 30_000,
    "FE1": 30_000,
    "FE2": 30_000,
    "FE3": 30_000,
    # Parcel Force express24
    "NDA": 30_000,
    "NDB": 30_000,
    "NDC": 30_000,
    "NDE": 30_000,
    # Special Delivery by time (1pm / 9am variants)
    "SD1": 2_000,
    "SD2": 2_000,
    "SD3": 2_000,
    "SD4": 2_000,
    "SD5": 2_000,
    "SD6": 2_000,
    "SDA": 2_000,
    "SDB": 2_000,
    "SDC": 2_000,
    "SDE": 2_000,
    "SDF": 2_000,
    "SDG": 2_000,
    "SDH": 2_000,
    "SDJ": 2_000,
    "SDK": 2_000,
    "SDM": 2_000,
    "SDN": 2_000,
    "SDQ": 2_000,
    # Special Delivery Guaranteed (end-of-day)
    "SDV": 10_000,
    "SDW": 10_000,
    "SDX": 10_000,
    "SDY": 10_000,
    "SDZ": 10_000,
    "SEA": 10_000,
    "SEB": 10_000,
    "SEC": 10_000,
    "SED": 10_000,
    # Account Mail
    "STL1": 2_000,
    "STL2": 2_000,
    # Tracked 24 / 48
    "TPN24": 20_000,
    "TPS48": 20_000,
    "TRN24": 20_000,
    "TRS48": 20_000,
}

# Parcel Force codes have a different dimension model to Royal Mail OBA codes.
_PARCEL_FORCE_CODES = frozenset(
    {"FE0", "FE1", "FE2", "FE3", "NDA", "NDB", "NDC", "NDE"}
)

# Per-service-code physical constraints (weight + dimensions).
# Royal Mail OBA: no side > 60 cm, L+W+D ≤ 90 cm.
# Parcel Force: longest side ≤ 150 cm, L+W+D ≤ 300 cm.
SERVICE_CONSTRAINTS: dict[str, ServiceConstraint] = {
    code: (
        ServiceConstraint(
            max_weight_g=30_000,
            max_combined_mm=3_000,
            max_length_mm=1_500,
        )
        if code in _PARCEL_FORCE_CODES
        else ServiceConstraint(
            max_weight_g=weight_g,
            max_combined_mm=900,
            max_single_side_mm=600,
        )
    )
    for code, weight_g in SERVICE_MAX_WEIGHT_G.items()
}
