"""Parser for Royal Mail OBA shipping option txt files.

OBA files differ from non-OBA files:
- No monetary values (prices are account-negotiated)
- Compensation may be "N/A" for account mail services
- An extra "Royal Mail OBA" brand line follows the data line
- Additional enhancements: Signed For, Local Collect, Delivery duty paid
- "Email/SMS notification" is a single compound token
"""

from __future__ import annotations

import re
from decimal import Decimal as D
from pathlib import Path
from typing import Optional

from .package_shipping_option import PackageShippingOption
from .format_dimensions import PACKAGE_FORMATS, SERVICE_DIMENSIONS

_COMP_PATTERN = re.compile(r"^\t(Up to £[\d.]+|N/A)")

# Maps OBA enhancement tokens to PackageShippingOption field names.
# "Email/SMS notification" is handled separately (maps to two fields).
_ENHANCEMENT_FIELDS: dict[str, str] = {
    "Tracked": "tracked",
    "Email notification": "email_notification",
    "SMS notification": "sms_notification",
    "Safeplace": "safeplace",
    "Age verified on delivery": "age_verified",
    "IOSS": "ioss",
    "Signed For included": "signed_for",
    "Signed For optional": "signed_for",
    "Local Collect": "local_collect",
    "Delivery duty paid": "ddp",
}


def _parse_enhancement_flags(s: str) -> dict[str, bool]:
    flags: dict[str, bool] = {
        "tracked": False,
        "email_notification": False,
        "sms_notification": False,
        "safeplace": False,
        "age_verified": False,
        "ioss": False,
        "signed_for": False,
        "local_collect": False,
        "ddp": False,
    }
    for token in (t.strip() for t in s.split(",")):
        if token == "Email/SMS notification":
            flags["email_notification"] = True
            flags["sms_notification"] = True
        elif token in _ENHANCEMENT_FIELDS:
            flags[_ENHANCEMENT_FIELDS[token]] = True
    return flags


def parse_oba_file(
    path: Path | str,
    package_size: str,
    max_weight_g: Optional[int] = None,
) -> list[PackageShippingOption]:
    """Parse an OBA shipping option txt file.

    The filename stem determines whether options are international:
    files ending in ``-GB`` are domestic; all others are international.

    Parameters:
        max_weight_g: Default service-level weight cap for every option in this
            file. Individual entries may be overridden via SERVICE_DIMENSIONS.
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
            line = lines[j]
            if line.strip() and not line.startswith("\t"):
                service = line.strip()
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
        if _COMP_PATTERN.match(next_line):
            delivery_speed = ""
            data_line = next_line
        else:
            delivery_speed = next_line.strip()
            i += 1
            while i < len(lines) and not _COMP_PATTERN.match(lines[i]):
                i += 1
            data_line = lines[i] if i < len(lines) else ""

        if not data_line or not _COMP_PATTERN.match(data_line):
            i += 1
            continue

        parts = data_line.split("\t")
        comp_str = parts[1].strip() if len(parts) > 1 else "N/A"
        if comp_str == "N/A":
            compensation = D("0.00")
        else:
            m = re.search(r"£([\d.]+)", comp_str)
            compensation = D(m.group(1)) if m else D("0.00")

        enhancements_str = parts[2].strip() if len(parts) > 2 else ""

        # Use per-service dimensions if available, else fall back to format default.
        dims = SERVICE_DIMENSIONS.get(service_code, fmt)

        options.append(
            PackageShippingOption(
                package_size_code=package_size,
                package_name=dims.name,
                package_max_weight_g=dims.max_weight_g,
                depth_mm=dims.depth_mm,
                width_mm=dims.width_mm,
                height_mm=dims.height_mm,
                max_sum_mm=dims.max_sum_mm,
                brand="Royal Mail OBA",
                service=service,
                service_code=service_code,
                delivery_speed=delivery_speed,
                compensation=compensation,
                gross=D("0.00"),
                international=international,
                is_oba=True,
                service_max_weight_g=max_weight_g,
                **_parse_enhancement_flags(enhancements_str),
            )
        )

        i += 1

    return options
