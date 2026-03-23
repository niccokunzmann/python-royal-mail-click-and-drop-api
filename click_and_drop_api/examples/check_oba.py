#!/usr/bin/env python
"""Check whether the account is an OBA (Online Business Account).

An OBA account has access to OBA-only service codes such as TPN24 (Tracked 24).
This is detected by attempting a test order with a service code — the order
is created and immediately deleted, so no shipment is made.
"""

from click_and_drop_api.simple import ClickAndDrop
import os

# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

if api.is_oba():
    print("This is an OBA account — OBA service codes are available.")
else:
    print("This is NOT an OBA account — only standard service codes are available.")
