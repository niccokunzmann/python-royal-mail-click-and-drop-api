#!/usr/bin/env python
"""Print package size and shipping cost with options."""

from click_and_drop_api.simple import packages_sizes

for package_size in packages_sizes:
    print("Package Code:", package_size.code)
    print("Package Name:", package_size.name)
    print("Package Max. Weight (grams):", package_size.weight_grams)
    print("Package Max. Height (mm):", package_size.height_mm)
    print("Package Max. Width (mm):", package_size.width_mm)
    print("Package Max. Length (mm):", package_size.length_mm)
    for shipping_option in package_size.shipping_options:
        print(
            f"\t{shipping_option.brand.ljust(14)} {shipping_option.service_code.ljust(10)} £{shipping_option.gross} \t{shipping_option.delivery_speed}"
        )
