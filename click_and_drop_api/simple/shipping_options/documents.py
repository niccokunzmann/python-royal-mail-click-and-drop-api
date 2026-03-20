"""Shipping options for OBA documents (international)."""

from pathlib import Path

from .oba_parser import parse_oba_file

_dir = Path(__file__).parent

options = [
    *parse_oba_file(_dir / "oba-codes" / "documents-DE.txt", "documents"),
]
