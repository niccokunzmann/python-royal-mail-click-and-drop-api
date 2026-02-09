#!/usr/bin/env python
from click_and_drop_api.simple import ClickAndDrop
import os

# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

example_order_id = 1002
example_order_reference = "my-ref-9999"

orders = api.get_specific_orders([example_order_id, example_order_reference])

for order in orders:
    print("Order Identifier:", order.order_identifier)
    print("Order Reference:", order.order_reference)
    print("Order Date:", order.order_date)
    print("Order Printed On:", order.printed_on)
    print("Order Manifested On:", order.manifested_on)
    print("Order Shipped On:", order.shipped_on)
    for package in order.packages:
        print("\tPackage Number:", package.package_number)
        print("\tPackage Tracking Number:", package.tracking_number)
