"""Shipping options for letters."""

from pathlib import Path

from .parser import parse_file
from .oba_parser import parse_oba_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "non-oba codes" / "letter-GB.txt", "letter"),
    *parse_file(_dir / "non-oba codes" / "letter-DE.txt", "letter"),
    *parse_oba_file(_dir / "oba-codes" / "letter-GB.txt", "letter"),
    *parse_oba_file(_dir / "oba-codes" / "letter-DE.txt", "letter"),
]
