# click_and_drop_api.CarriersApi

All URIs are relative to *http://api.parcel.royalmail.com/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_carriers_async**](CarriersApi.md#get_carriers_async) | **GET** /carriers | Retrieve list of carriers for the account


# **get_carriers_async**
> List[GetCarrierResource] get_carriers_async()

Retrieve list of carriers for the account

### Example

* Api Key Authentication (Bearer):

```python
import click_and_drop_api
from click_and_drop_api.models.get_carrier_resource import GetCarrierResource
from click_and_drop_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://api.parcel.royalmail.com/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = click_and_drop_api.Configuration(
    host = "http://api.parcel.royalmail.com/api/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: Bearer
configuration.api_key['Bearer'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Bearer'] = 'Bearer'

# Enter a context with an instance of the API client
with click_and_drop_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = click_and_drop_api.CarriersApi(api_client)

    try:
        # Retrieve list of carriers for the account
        api_response = api_instance.get_carriers_async()
        print("The response of CarriersApi->get_carriers_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CarriersApi->get_carriers_async: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[GetCarrierResource]**](GetCarrierResource.md)

### Authorization

[Bearer](api.md#Bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return list of carriers |  -  |
**401** | Unauthorized |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to Model list]](api.md#documentation-for-models) [[Back to README]](api.md)

