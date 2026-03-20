"""Shipping options for large letters."""

from pathlib import Path

from .parser import parse_file
from .oba_parser import parse_oba_file

_dir = Path(__file__).parent

options = [
    *parse_file(_dir / "non-oba codes" / "large_letter-GB.txt", "largeLetter"),
    *parse_file(_dir / "non-oba codes" / "large_letter-DE.txt", "largeLetter"),
    *parse_oba_file(
        _dir / "oba-codes" / "large_letter-GB.txt", "largeLetter", max_weight_g=750
    ),
    *parse_oba_file(
        _dir / "oba-codes" / "large_letter-DE.txt", "largeLetter", max_weight_g=750
    ),
]
