# click_and_drop_api.ReturnsApi

All URIs are relative to *http://api.parcel.royalmail.com/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**returns_post**](ReturnsApi.md#returns_post) | **POST** /returns | Create a return shipment
[**returns_services_get**](ReturnsApi.md#returns_services_get) | **GET** /returns/services | List available return services


# **returns_post**
> CreateReturnResponse returns_post(body)

Create a return shipment

Creates a return label and returns shipment details including tracking number, QR code, and label.

### Example

* Api Key Authentication (Bearer):

```python
import click_and_drop_api
from click_and_drop_api.models.create_return_request import CreateReturnRequest
from click_and_drop_api.models.create_return_response import CreateReturnResponse
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
    api_instance = click_and_drop_api.ReturnsApi(api_client)
    body = click_and_drop_api.CreateReturnRequest() # CreateReturnRequest | Return creation request

    try:
        # Create a return shipment
        api_response = api_instance.returns_post(body)
        print("The response of ReturnsApi->returns_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReturnsApi->returns_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CreateReturnRequest**](CreateReturnRequest.md)| Return creation request | 

### Return type

[**CreateReturnResponse**](CreateReturnResponse.md)

### Authorization

[Bearer](api.md#Bearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully created return shipment |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to Model list]](api.md#documentation-for-models) [[Back to README]](api.md)

# **returns_services_get**
> GetServicesResponse returns_services_get()

List available return services

Returns a list of return services that can be used when creating return shipments.

### Example

* Api Key Authentication (Bearer):

```python
import click_and_drop_api
from click_and_drop_api.models.get_services_response import GetServicesResponse
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
    api_instance = click_and_drop_api.ReturnsApi(api_client)

    try:
        # List available return services
        api_response = api_instance.returns_services_get()
        print("The response of ReturnsApi->returns_services_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReturnsApi->returns_services_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetServicesResponse**](GetServicesResponse.md)

### Authorization

[Bearer](api.md#Bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Lists all available return services for generating return labels |  -  |
**401** | Unauthorized |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to Model list]](api.md#documentation-for-models) [[Back to README]](api.md)

