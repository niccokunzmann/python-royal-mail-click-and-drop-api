#!/usr/bin/env python3
"""Creates one order per parcel type, reports whether it holds over 2 kg, then deletes it.
Also prints which OBA parcel service codes allow 3 kg and which do not.

Usage:
    API_KEY=<your-key> python scripts/test_parcel_orders.py
"""

import os
import sys
from datetime import datetime, timezone

from click_and_drop_api.simple.api import ClickAndDrop
from click_and_drop_api.simple.types import (
    Address,
    CreateOrder,
    PostageDetails,
    RecipientDetails,
)
from click_and_drop_api.simple.shipping.small_parcel import (
    options as small_parcel_options,
)
from click_and_drop_api.simple.shipping.medium_parcel import (
    options as medium_parcel_options,
)
from click_and_drop_api.simple.shipping.large_parcel import (
    options as large_parcel_options,
)
from click_and_drop_api.simple.shipping.parcel import (
    options as oba_parcel_options,
    SERVICE_MAX_WEIGHT_G as OBA_PARCEL_SERVICE_MAX_WEIGHT_G,
)

# (label, options, max_weight_g)
# Falls back to oba_parcel_options when a non-OBA module has no entries yet.
_PARCEL_TYPES = [
    ("Small Parcel", small_parcel_options or oba_parcel_options, 2_000),
    ("Medium Parcel", medium_parcel_options or oba_parcel_options, 20_000),
    ("Large Parcel", large_parcel_options or oba_parcel_options, 30_000),
    ("OBA Parcel", oba_parcel_options, 30_000),
]


def _make_order(service_code: str) -> CreateOrder:
    return CreateOrder(
        orderDate=datetime.now(timezone.utc),
        subtotal=10.00,
        shippingCostCharged=0.00,
        total=10.00,
        currencyCode="GBP",
        recipient=RecipientDetails(
            address=Address(
                fullName="Test User",
                addressLine1="1 Test Street",
                city="London",
                postcode="SW1A 1AA",
                countryCode="GB",
            )
        ),
        postageDetails=PostageDetails(serviceCode=service_code),
    )


def main() -> None:
    key = os.environ.get("API_KEY")
    if not key:
        sys.exit("API_KEY environment variable is not set")

    api = ClickAndDrop(key)

    for label, options, max_w in _PARCEL_TYPES:
        option = next((o for o in options if not o.international), None)
        if option is None:
            print(f"{label}: no domestic option found, skipping\n")
            continue

        over_2kg = max_w > 2_000

        print(f"{label} ({option.service_code})")
        print(f"  max weight : {max_w:,}g")
        print(f"  over 2 kg  : {over_2kg}")

        response = api.create_order(_make_order(option.service_code))

        if not response.created_orders:
            errors = [
                e2.error_message for e1 in response.failed_orders for e2 in e1.errors
            ]
            print(f"  create     : FAILED — {'; '.join(errors)}\n")
            continue

        order_id = response.created_orders[0].order_identifier
        print(f"  created    : order {order_id}")

        api.delete_orders(order_id)
        print(f"  deleted    : order {order_id}\n")

    # --- OBA parcel 3 kg capability report ---
    test_weight = 11_000
    print(f"OBA parcel service codes — allows {test_weight:,}g:")
    domestic_oba = [o for o in oba_parcel_options if not o.international]
    allows, rejects = [], []
    for option in domestic_oba:
        limit = OBA_PARCEL_SERVICE_MAX_WEIGHT_G.get(option.service_code)
        if limit is None:
            continue
        (allows if limit >= test_weight else rejects).append(
            (option.service_code, limit)
        )
    print(
        f"  YES ({len(allows)}): {', '.join(f'{c} ({w // 1000}kg)' for c, w in allows)}"
    )
    print(
        f"  NO  ({len(rejects)}): {', '.join(f'{c} ({w // 1000}kg)' for c, w in rejects)}"
    )


if __name__ == "__main__":
    main()
