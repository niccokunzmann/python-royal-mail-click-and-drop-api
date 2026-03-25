"""Shipping options for small parcels."""

from pathlib import Path

from .parser import parse_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "non-oba codes" / "small_parcel-GB.txt", "smallParcel"),
    *parse_file(_dir / "non-oba codes" / "small_parcel-DE.txt", "smallParcel"),
]
