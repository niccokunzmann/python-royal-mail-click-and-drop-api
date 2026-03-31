#!/usr/bin/env python
"""Print all countries that accept a given service code.

Uses test_shipping internally: a test order is created and immediately deleted
for each country, so no real shipments are made.

Arguments:

- service code (optional, defaults to OLP1)
"""

import os
import sys

from click_and_drop_api.simple import ClickAndDrop

API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

PACKAGE_SIZE = "letter"
SERVICE_CODE = "OLP1" if len(sys.argv) == 1 else sys.argv[1]

countries = api.get_countries_for_shipping(
    package_size=PACKAGE_SIZE,
    service_code=SERVICE_CODE,
    weight_in_grams=50,
)

print(f"{PACKAGE_SIZE} with {SERVICE_CODE} ships to {len(countries)} countries:")
print(", ".join(countries))
