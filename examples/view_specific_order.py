#!/usr/bin/env python
from datetime import datetime
from pathlib import Path
import time
import click_and_drop_api
from click_and_drop_api.rest import ApiException
from pprint import pprint
import os

configuration = click_and_drop_api.Configuration(
    host = "https://api.parcel.royalmail.com/api/v1"
)


# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
configuration.api_key['Bearer'] = os.environ.get("API_KEY") or Path("api-key.txt").read_text().strip()

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Bearer'] = 'Bearer'


# Enter a context with an instance of the API client
with click_and_drop_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = click_and_drop_api.OrdersApi(api_client)

    response = api_instance.get_specific_orders_async(order_identifiers='1001;1002')
    for order in response:
        print("Order Identifier:", order.order_identifier)
        print("Order Reference:", order.order_reference)
        print("Order Date:", order.order_date)
        print("Order Printed On:", order.printed_on)
        print("Order Manifested On:", order.manifested_on)
        print("Order Shipped On:", order.shipped_on)
        for package in order.packages:
            print("\tPackage Number:", package.package_number)
            print("\tPackage Tracking Number:", package.tracking_number)
