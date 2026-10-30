# click_and_drop_api.OlpServicesApi

All URIs are relative to *http://api.parcel.royalmail.com/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**services_olp_get**](OlpServicesApi.md#services_olp_get) | **GET** /services/olp | List available Royal Mail OLP shipping services


# **services_olp_get**
> OlpServicesResult services_olp_get(country, weight=weight, postcode=postcode, package_format=package_format)

List available Royal Mail OLP shipping services

Returns the Royal Mail OLP shipping services available for a destination country, optionally narrowed by weight, postcode and/or package format.

### Example

* Api Key Authentication (Bearer):

```python
import click_and_drop_api
from click_and_drop_api.models.olp_services_result import OlpServicesResult
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
    api_instance = click_and_drop_api.OlpServicesApi(api_client)
    country = 'country_example' # str | ISO 3166-1 alpha-3 destination country code. Must be a recognised ISO 3166-1 alpha-3 code — an unrecognised value returns a 400.
    weight = 56 # int | Package weight in grams. (optional)
    postcode = 'postcode_example' # str | Recipient postcode. (optional)
    package_format = 'package_format_example' # str | Package format to filter results by. Applied to the results returned by Royal Mail OLP — it isn't sent to Royal Mail OLP itself, which has no equivalent filter on this call. (optional)

    try:
        # List available Royal Mail OLP shipping services
        api_response = api_instance.services_olp_get(country, weight=weight, postcode=postcode, package_format=package_format)
        print("The response of OlpServicesApi->services_olp_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OlpServicesApi->services_olp_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **country** | **str**| ISO 3166-1 alpha-3 destination country code. Must be a recognised ISO 3166-1 alpha-3 code — an unrecognised value returns a 400. | 
 **weight** | **int**| Package weight in grams. | [optional] 
 **postcode** | **str**| Recipient postcode. | [optional] 
 **package_format** | **str**| Package format to filter results by. Applied to the results returned by Royal Mail OLP — it isn&#39;t sent to Royal Mail OLP itself, which has no equivalent filter on this call. | [optional] 

### Return type

[**OlpServicesResult**](OlpServicesResult.md)

### Authorization

[Bearer](api.md#Bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Lists the available Royal Mail OLP shipping services for the given destination |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden (Royal Mail OLP is not configured for this account) |  -  |
**500** | Internal Server Error |  -  |
**503** | The Royal Mail OLP service is currently unavailable |  -  |

[[Back to top]](#) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to Model list]](api.md#documentation-for-models) [[Back to README]](api.md)

