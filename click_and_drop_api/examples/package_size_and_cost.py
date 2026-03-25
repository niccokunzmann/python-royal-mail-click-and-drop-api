#!/usr/bin/env python
"""Print package size and shipping cost with options."""

from click_and_drop_api.simple import db

# Iterate package sizes in insertion order, then list each service under it
seen: dict = {}
for _o in db:
    if _o.package_size_code not in seen:
        seen[_o.package_size_code] = _o

for package_size_code, first in seen.items():
    print("Package Code:", first.package_size_code)
    print("Package Name:", first.package_name)
    print("Package Max. Weight (grams):", first.package_max_weight_g)
    print("Package Max. Height (mm):", first.height_mm)
    print("Package Max. Width (mm):", first.width_mm)
    print("Package Max. Length (mm):", first.depth_mm)
    for option in db.for_package_size(package_size_code):
        print(
            f"\t{option.brand.ljust(14)} {option.service_code.ljust(10)} £{option.gross} \t{option.delivery_speed}"
        )
