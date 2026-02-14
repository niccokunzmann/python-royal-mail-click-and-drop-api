#!/usr/bin/env python
"""Generate a label for an order number.

The order has to be created first.
You can use create_order.py to create an order.

View your orders: https://business.parcel.royalmail.com/orders/

Note: Label generation is only possible for OBA customers
"""

from click_and_drop_api.simple import ClickAndDrop
import os
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print(
        f"""{Path(__file__).name} [ORDER_NUMBER_OR_REFERENCE]

    ORDER_NUMBER_OR_REFERENCE: The order number or reference.   
    """
    )
    print(__doc__)
    exit(0)

# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

order_id = sys.argv[1]
if order_id.isdigit():
    order_id = int(order_id)

label = api.get_label(order_id, "postageLabel", include_returns_label=False)

(Path(__file__).parent / "label.pdf").write_bytes(label)
