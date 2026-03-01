"""Shipping options for letters."""

from pathlib import Path

from .parser import parse_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "letter-GB.txt", "letter"),
    *parse_file(_dir / "letter-DE.txt", "letter"),
]
