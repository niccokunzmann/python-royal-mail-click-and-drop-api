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

    request = click_and_drop_api.CreateOrdersRequest(
        [
            click_and_drop_api.CreateOrderRequest(
                orderReference="ORDER-REF-123",
                orderDate=datetime(2026, 1, 1),
                billing_details=click_and_drop_api.BillingDetailsRequest(
                    address=click_and_drop_api.AddressRequest(
                        fullName="John Doe",
                        companyName="",
                        addressLine1="1 Example Street",
                        addressLine2="",
                        addressLine3="",
                        city="London",
                        # county="",
                        postcode="SA1 97EE",
                    ),
                )
        )]
    ) # CreateOrdersRequest | 

    try:
        # Create orders
        api_response = api_instance.create_orders_async(request)
        print("The response of OrdersApi->create_orders_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->create_orders_async: %s\n" % e)