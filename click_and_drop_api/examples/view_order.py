#!/usr/bin/env python
"""Print details of a single order by order number or reference.

Usage::

    python -m click_and_drop_api.examples.view_order <order_id_or_reference>
"""

import os
import sys

from click_and_drop_api.simple import ClickAndDrop

API_KEY = os.environ["API_KEY"]

if len(sys.argv) != 2:
    print(
        "Usage: python -m click_and_drop_api.examples.view_order <order_id_or_reference>"
    )
    sys.exit(1)

identifier = sys.argv[1]
# treat numeric strings as integer order IDs
if identifier.isdigit():
    identifier = int(identifier)

api = ClickAndDrop(API_KEY)
order = api.get_order(identifier)

if order is None:
    print(f"Order not found: {identifier!r}")
    sys.exit(1)

print(f"Order identifier : {order.order_identifier}")
print(f"Order reference  : {order.order_reference}")
print(f"Created on       : {order.created_on}")
print(f"Order date       : {order.order_date}")
print(f"Printed on       : {order.printed_on}")
print(f"Manifested on    : {order.manifested_on}")
print(f"Shipped on       : {order.shipped_on}")
print(f"Tracking number  : {order.tracking_number}")

if order.packages:
    print(f"Packages ({len(order.packages)}):")
    for pkg in order.packages:
        print(f"  #{pkg.package_number}  tracking: {pkg.tracking_number}")
