"""Parser for Royal Mail shipping option txt files."""

from __future__ import annotations

import re
from decimal import Decimal as D
from pathlib import Path

from .model import ShippingOption

_ENHANCEMENT_FIELDS: dict[str, str] = {
    "Tracked": "tracked",
    "Email notification": "email_notification",
    "SMS notification": "sms_notification",
    "Safeplace": "safeplace",
    "Age verified on delivery": "age_verified",
    "IOSS": "ioss",
}


def _parse_enhancement_flags(s: str) -> dict[str, bool]:
    parts = {f.strip() for f in s.split(",")}
    return {field: key in parts for key, field in _ENHANCEMENT_FIELDS.items()}


def _extract_decimal(s: str) -> D:
    m = re.search(r"£([\d.]+)", s)
    return D(m.group(1)) if m else D("0.00")


def parse_file(path: Path | str, package_size: str) -> list[ShippingOption]:
    """Parse a shipping option txt file and return a list of ShippingOption objects.

    The filename stem determines whether options are international:
    files ending in ``-GB`` are domestic; all others are international.
    """
    path = Path(path)
    international = not path.stem.endswith("-GB")
    lines = path.read_text().splitlines()
    options = []

    i = 0
    while i < len(lines):
        if lines[i].strip() != "See details":
            i += 1
            continue

        # Service name: last line before "See details" matching "(£N"
        service = ""
        for j in range(i - 1, -1, -1):
            line = lines[j].strip()
            if line and re.search(r"\(£\d", line):
                service = line
                break

        # Service code: first non-empty line after "See details"
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        code_line = lines[i].strip() if i < len(lines) else ""
        service_code = code_line.split()[0] if code_line else ""

        # Next non-empty line: delivery speed or data line
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            break

        next_line = lines[i]
        if "Up to" in next_line:
            delivery_speed = ""
            data_line = next_line
        else:
            delivery_speed = next_line.strip()
            i += 1
            while i < len(lines) and "Up to" not in lines[i]:
                i += 1
            data_line = lines[i] if i < len(lines) else ""

        if not data_line or "Up to" not in data_line:
            i += 1
            continue

        # Data line format: \tUp to £{comp}\t{enhancements}\t£{net}\t£{tax}\t£{gross}
        parts = data_line.split("\t")
        compensation = _extract_decimal(parts[1]) if len(parts) > 1 else D("0.00")
        enhancements_str = parts[2].strip() if len(parts) > 2 else ""
        tax = _extract_decimal(parts[4]) if len(parts) > 4 else D("0.00")
        gross = _extract_decimal(parts[5]) if len(parts) > 5 else D("0.00")

        brand = "Parcel Force" if service_code.startswith("PF") else "Royal Mail"

        options.append(
            ShippingOption(
                package_size=package_size,
                brand=brand,
                service=service,
                service_code=service_code,
                delivery_speed=delivery_speed,
                compensation=compensation,
                gross=gross,
                tax=tax,
                international=international,
                **_parse_enhancement_flags(enhancements_str),
            )
        )

        i += 1

    return options
