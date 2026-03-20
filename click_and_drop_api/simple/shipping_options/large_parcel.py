"""Shipping options for large parcels."""

from pathlib import Path

from .parser import parse_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "non-oba codes" / "large_parcel-GB.txt", "largeParcel"),
    *parse_file(_dir / "non-oba codes" / "large_parcel-DE.txt", "largeParcel"),
]
