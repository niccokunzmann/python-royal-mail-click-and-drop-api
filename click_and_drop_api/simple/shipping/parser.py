"""Parser for Royal Mail (non-OBA) shipping option txt files."""

from __future__ import annotations

import re
from decimal import Decimal as D
from pathlib import Path

from .package_shipping_option import PackageShippingOption
from .format_dimensions import PACKAGE_FORMATS

_UP_TO = "Up to"

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


def parse_file(path: Path | str, package_size: str) -> list[PackageShippingOption]:
    """Parse a non-OBA shipping option txt file.

    The filename stem determines whether options are international:
    files ending in ``-GB`` are domestic; all others are international.
    """
    path = Path(path)
    international = not path.stem.endswith("-GB")
    lines = path.read_text().splitlines()
    fmt = PACKAGE_FORMATS[package_size]
    options = []

    i = 0
    while i < len(lines):
        if lines[i].strip() != "See details":
            i += 1
            continue

        service = ""
        for j in range(i - 1, -1, -1):
            line = lines[j].strip()
            if line and re.search(r"\(£\d", line):
                service = line
                break

        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        code_line = lines[i].strip() if i < len(lines) else ""
        service_code = code_line.split()[0] if code_line else ""

        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            break

        next_line = lines[i]
        if _UP_TO in next_line:
            delivery_speed = ""
            data_line = next_line
        else:
            delivery_speed = next_line.strip()
            i += 1
            while i < len(lines) and _UP_TO not in lines[i]:
                i += 1
            data_line = lines[i] if i < len(lines) else ""

        if not data_line or _UP_TO not in data_line:
            i += 1
            continue

        parts = data_line.split("\t")
        compensation = _extract_decimal(parts[1]) if len(parts) > 1 else D("0.00")
        enhancements_str = parts[2].strip() if len(parts) > 2 else ""
        tax = _extract_decimal(parts[4]) if len(parts) > 4 else D("0.00")
        gross = _extract_decimal(parts[5]) if len(parts) > 5 else D("0.00")

        brand = "Parcel Force" if service_code.startswith("PF") else "Royal Mail"

        options.append(
            PackageShippingOption(
                package_size_code=package_size,
                package_name=fmt.name,
                package_max_weight_g=fmt.max_weight_g,
                depth_mm=fmt.depth_mm,
                width_mm=fmt.width_mm,
                height_mm=fmt.height_mm,
                max_sum_mm=fmt.max_sum_mm,
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
