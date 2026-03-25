"""Shipping options for medium parcels."""

from pathlib import Path

from .parser import parse_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "non-oba codes" / "medium_parcel-GB.txt", "mediumParcel"),
    *parse_file(_dir / "non-oba codes" / "medium_parcel-DE.txt", "mediumParcel"),
]
