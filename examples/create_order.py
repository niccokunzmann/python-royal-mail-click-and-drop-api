#!/usr/bin/env python
from click_and_drop_api.simple import (
    ClickAndDrop,
    CreateOrder,
    RecipientDetails,
    Address,
)
import os
from datetime import datetime, UTC

# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

REFERENCE = "example-order-from-python-api"

new_order = CreateOrder(
    order_reference=REFERENCE,
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
        address_book_reference="",
    ),
    order_date=datetime.now(UTC),
    subtotal=12,
    shipping_cost_charged=3,
    total=15,
)

response = api.create_orders(new_order)

print(f"Orders created: {response.created_orders}")
print(f"Errors: {response.errors_count}")

print("Getting the order from the API.")
orders = api.get_orders([REFERENCE])

for order in orders:
    print(f"Order Reference: {order.order_reference}")
    print(f"Order Identifier: {order.order_identifier}")

print("Deleting order.")

deleted_orders = api.delete_orders([REFERENCE])

print(f"Orders deleted: {deleted_orders.deleted_orders}")
print(f"Errors: {deleted_orders.errors}")
