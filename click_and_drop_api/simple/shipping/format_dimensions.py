"""Package format physical constraints.

Kept in a standalone module (no imports from this package) so both
parsers and package_sizes can import it without circular dependencies.
"""

from __future__ import annotations
from typing import NamedTuple, Optional


class FormatDimensions(NamedTuple):
    """Physical constraints for a package format."""

    name: str
    max_weight_g: int
    depth_mm: int
    width_mm: int
    height_mm: int
    # Royal Mail OBA parcel and Parcel Force use a combined L+W+D limit.
    max_sum_mm: Optional[int] = None


# Parcel Force dimensions used for FE*/ND* service codes within "parcel" format.
_PF = FormatDimensions("Parcel", 30_000, 1500, 3000, 3000, 3000)

PACKAGE_FORMATS: dict[str, FormatDimensions] = {
    "letter": FormatDimensions("Letter", 100, 240, 165, 5),
    "largeLetter": FormatDimensions("Large letter", 1_000, 353, 250, 25),
    "smallParcel": FormatDimensions("Small parcel", 2_000, 450, 350, 160),
    "mediumParcel": FormatDimensions("Medium parcel", 20_000, 610, 460, 460),
    "largeParcel": FormatDimensions("Large parcel", 30_000, 1500, 3000, 3000),
    # OBA Royal Mail parcel: no single side > 60 cm, L+W+D ≤ 90 cm.
    "parcel": FormatDimensions("Parcel", 30_000, 600, 600, 600, 900),
    "documents": FormatDimensions("Documents", 30_000, 1500, 3000, 3000),
}

# Service codes whose physical constraints differ from their format default.
# Parcel Force express services live in the "parcel" format but follow PF rules.
SERVICE_DIMENSIONS: dict[str, FormatDimensions] = {
    code: _PF for code in ("FE0", "FE1", "FE2", "FE3", "NDA", "NDB", "NDC", "NDE")
}

__all__ = [
    "FormatDimensions",
    "PACKAGE_FORMATS",
    "SERVICE_DIMENSIONS",
]
