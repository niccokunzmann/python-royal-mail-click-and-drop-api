"""Shipping options for large letters."""

from pathlib import Path

from .parser import parse_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "large_letter-GB.txt", "largeLetter"),
    *parse_file(_dir / "large_letter-DE.txt", "largeLetter"),
]
