#!/usr/bin/env python
from click_and_drop_api.simple import (
    ClickAndDrop,
    CreateOrder,
    RecipientDetails,
    Address,
    PackageSize,
)
import os
from datetime import datetime, UTC

# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

# choose a new reference or else the API will reject the order
REFERENCE = "example-order-{now}".format(now=datetime.now(UTC).strftime("%Y%m%d%H%M%S"))

package = PackageSize.get("letter")  # send a letter
service = package.get_shipping_option("OLP2")  # with 2nd class delivery

new_order = CreateOrder(
    order_reference=REFERENCE,
    is_recipient_a_business=False,
    recipient=RecipientDetails(
        address=Address(
            full_name="Nicco Kunzmann",
            company_name="",
            address_line1="Wernlas",
            address_line2="Talley",
            address_line3="",
            city="Llandeilo",
            county="United Kingdom",
            postcode="SA19 7EE",
            country_code="GB",
        ),
        phone_number="07726640000",
        email_address="niccokunzmann@rambler.ru",
    ),
    order_date=datetime.now(UTC),
    subtotal=float(12),  # 12 pounds
    shipping_cost_charged=float(service.gross),  # charge the same as Royal Mail
    total=float(12 + service.gross),
    currency_code="GBP",
    # postage_details=service.as_postage_details(),
    packages=[package.as_package_request(weight_in_grams=80)],
)

response = api.create_orders(new_order)

print(f"Orders created: {response.created_orders}")
print(f"Errors: {response.errors_count}")

print("Getting the order from the API.")
order = api.get_order(REFERENCE)

print(f"Order Reference: {order.order_reference}")
print(f"Order Identifier: {order.order_identifier}")

# Delete the order when run in CI test
if "CI" in os.environ:
    print("Deleting order.")

    deleted_orders = api.delete_orders([REFERENCE])

    print(f"Orders deleted: {deleted_orders.deleted_orders}")
    print(f"Errors: {deleted_orders.errors}")
