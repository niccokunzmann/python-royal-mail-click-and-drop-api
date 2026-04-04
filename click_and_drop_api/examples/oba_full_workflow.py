#!/usr/bin/env python
"""Full OBA workflow: create a cheap domestic order, generate a label,
apply postage via manifest, and mark the order as despatched.

Steps performed:
  1. Verify the account is OBA (required for label generation and OBA services)
  2. Pick the cheapest domestic OBA service
  3. Create the order (with label generation requested at creation time)
  4. Save the label PDF to disk
  5. Manifest eligible orders (applies postage)
  6. Set the order status to "despatched"

Note: Label generation is only available for OBA customers.
"""

import os
import sys
from datetime import datetime, UTC
from pathlib import Path

from click_and_drop_api.simple import (
    ClickAndDrop,
    CreateOrder,
    LabelGeneration,
    RecipientDetails,
    Address,
    db,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ["API_KEY"]
REFERENCE = "oba-workflow-{now}".format(now=datetime.now(UTC).strftime("%Y%m%d%H%M%S"))
WEIGHT_GRAMS = 100

api = ClickAndDrop(API_KEY)

# ---------------------------------------------------------------------------
# Step 1: verify OBA
# ---------------------------------------------------------------------------

print("Checking account type…")
if not api.is_oba():
    print("ERROR: This account is not OBA. Label generation requires an OBA account.")
    sys.exit(1)
print("Account is OBA.")

# ---------------------------------------------------------------------------
# Step 2: pick cheapest domestic OBA service
# ---------------------------------------------------------------------------

cheapest = db.filter(is_oba=True, international=False).any_or_none
if cheapest is None:
    print("ERROR: No domestic OBA service found in the shipping database.")
    sys.exit(1)

print(
    f"Using service: {cheapest.brand} {cheapest.service_code}"
    f" ({cheapest.delivery_speed}) — £{cheapest.gross}"
)

# ---------------------------------------------------------------------------
# Step 3: create the order, requesting a label in the response
# ---------------------------------------------------------------------------

order = CreateOrder(
    order_reference=REFERENCE,
    recipient=RecipientDetails(
        address=Address(
            full_name="Nicco Kunzmann",
            address_line1="1 Test Street",
            city="London",
            postcode="SW1A 1AA",
            country_code="GB",
        )
    ),
    order_date=datetime.now(UTC),
    subtotal=1.00,
    shipping_cost_charged=float(cheapest.gross),
    total=1.00 + float(cheapest.gross),
    currency_code="GBP",
    postage_details=cheapest.as_postage_details(),
    packages=[cheapest.as_package_request(weight_in_grams=WEIGHT_GRAMS)],
    label=LabelGeneration(
        include_label_in_response=True,
        include_cn=False,
        include_returns_label=False,
    ),
)

print(f"Creating order {REFERENCE!r}…")
response = api.create_order(order)

if response.errors_count or not response.created_orders:
    print(f"ERROR: Order creation failed: {response.failed_orders}")
    sys.exit(1)

created = response.created_orders[0]
order_id = created.order_identifier
print(f"Order created: id={order_id}, reference={created.order_reference}")

# ---------------------------------------------------------------------------
# Step 4: save label PDF
# ---------------------------------------------------------------------------

print("Fetching label…")
label_pdf = api.get_label(order_id, "postageLabel", include_returns_label=False)
label_path = Path(__file__).parent / "label.pdf"
label_path.write_bytes(label_pdf)
print(f"Label saved to {label_path}")

# ---------------------------------------------------------------------------
# Step 5: manifest (applies postage)
# ---------------------------------------------------------------------------

print("Manifesting eligible orders…")
manifest = api.manifest_orders()
print(f"Manifest number: {manifest.manifest_number}")
if manifest.pdf is not None:
    manifest_path = Path(__file__).parent / "manifest.pdf"
    manifest_path.write_bytes(manifest.pdf)
    print(f"Manifest PDF saved to {manifest_path}")

# ---------------------------------------------------------------------------
# Step 6: mark as despatched
# ---------------------------------------------------------------------------

print(f"Setting order {order_id} to 'despatched'…")
update = api.update_orders([order_id], status="despatched")

if update.errors:
    print(f"WARNING: status update errors: {update.errors}")
else:
    print("Order marked as despatched.")

print("Done.")
