# click_and_drop_api.VersionApi

All URIs are relative to *http://api.parcel.royalmail.com/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_version_async**](VersionApi.md#get_version_async) | **GET** /version | Get API version details.


# **get_version_async**
> GetVersionResource get_version_async()

Get API version details.

### Example


```python
import click_and_drop_api
from click_and_drop_api.models.get_version_resource import GetVersionResource
from click_and_drop_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://api.parcel.royalmail.com/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = click_and_drop_api.Configuration(
    host = "http://api.parcel.royalmail.com/api/v1"
)


# Enter a context with an instance of the API client
with click_and_drop_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = click_and_drop_api.VersionApi(api_client)

    try:
        # Get API version details.
        api_response = api_instance.get_version_async()
        print("The response of VersionApi->get_version_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionApi->get_version_async: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetVersionResource**](GetVersionResource.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns details about the API version |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](./#documentation-for-api-endpoints) [[Back to Model list]](./#documentation-for-models) [[Back to README]](./)

