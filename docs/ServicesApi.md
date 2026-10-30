# click_and_drop_api.ServicesApi

All URIs are relative to *http://api.parcel.royalmail.com/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_services_async**](ServicesApi.md#get_services_async) | **GET** /services | Retrieve list of available services for the account, optionally filtered by carrier, destination and package


# **get_services_async**
> List[GetCarrierServicesResource] get_services_async(destination_country_code=destination_country_code, destination_postcode=destination_postcode, packaging_format=packaging_format, package_weight=package_weight, carrier_guid=carrier_guid, carrier_name=carrier_name)

Retrieve list of available services for the account, optionally filtered by carrier, destination and package

### Example

* Api Key Authentication (Bearer):

```python
import click_and_drop_api
from click_and_drop_api.models.get_carrier_services_resource import GetCarrierServicesResource
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
    api_instance = click_and_drop_api.ServicesApi(api_client)
    destination_country_code = 'destination_country_code_example' # str | ISO 3166-1 alpha-3 country code of the shipment destination (e.g. GBR). Must be a recognised ISO 3166-1 alpha-3 code — an unrecognised value returns a 400. Supply it to scope results to a single destination (e.g. before checkout); GBR additionally requires destinationPostcode to be set. Omit it (along with destinationPostcode, packagingFormat and packageWeight) to browse the full, unfiltered service catalogue for discovery. destinationPostcode, packagingFormat and packageWeight require destinationCountryCode to also be supplied — providing any of them without it returns a 400, since the underlying carrier lookup can only be filtered once a destination is known. (optional)
    destination_postcode = 'destination_postcode_example' # str | Postcode of the shipment destination. Required when destinationCountryCode is GBR — a 400 is returned if it's missing or blank. For any other destination country, postcode-based filtering isn't supported, so this value is ignored even if supplied. (optional)
    packaging_format = 'packaging_format_example' # str | Packaging format of the shipment. Requires destinationCountryCode to also be supplied — a 400 is returned otherwise. (optional)
    package_weight = 56 # int | Weight of the package in grams. Requires destinationCountryCode to also be supplied — a 400 is returned otherwise. (optional)
    carrier_guid = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | GUID of a carrier configured on the account, to scope results to that carrier only. An unrecognised carrierGuid returns a 400. If carrierName is also supplied, both must refer to the same carrier. (optional)
    carrier_name = 'carrier_name_example' # str | Name of a carrier configured on the account, to scope results to that carrier only. An unrecognised carrierName returns a 400. If carrierGuid is also supplied, both must refer to the same carrier. (optional)

    try:
        # Retrieve list of available services for the account, optionally filtered by carrier, destination and package
        api_response = api_instance.get_services_async(destination_country_code=destination_country_code, destination_postcode=destination_postcode, packaging_format=packaging_format, package_weight=package_weight, carrier_guid=carrier_guid, carrier_name=carrier_name)
        print("The response of ServicesApi->get_services_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ServicesApi->get_services_async: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_country_code** | **str**| ISO 3166-1 alpha-3 country code of the shipment destination (e.g. GBR). Must be a recognised ISO 3166-1 alpha-3 code — an unrecognised value returns a 400. Supply it to scope results to a single destination (e.g. before checkout); GBR additionally requires destinationPostcode to be set. Omit it (along with destinationPostcode, packagingFormat and packageWeight) to browse the full, unfiltered service catalogue for discovery. destinationPostcode, packagingFormat and packageWeight require destinationCountryCode to also be supplied — providing any of them without it returns a 400, since the underlying carrier lookup can only be filtered once a destination is known. | [optional] 
 **destination_postcode** | **str**| Postcode of the shipment destination. Required when destinationCountryCode is GBR — a 400 is returned if it&#39;s missing or blank. For any other destination country, postcode-based filtering isn&#39;t supported, so this value is ignored even if supplied. | [optional] 
 **packaging_format** | **str**| Packaging format of the shipment. Requires destinationCountryCode to also be supplied — a 400 is returned otherwise. | [optional] 
 **package_weight** | **int**| Weight of the package in grams. Requires destinationCountryCode to also be supplied — a 400 is returned otherwise. | [optional] 
 **carrier_guid** | **UUID**| GUID of a carrier configured on the account, to scope results to that carrier only. An unrecognised carrierGuid returns a 400. If carrierName is also supplied, both must refer to the same carrier. | [optional] 
 **carrier_name** | **str**| Name of a carrier configured on the account, to scope results to that carrier only. An unrecognised carrierName returns a 400. If carrierGuid is also supplied, both must refer to the same carrier. | [optional] 

### Return type

[**List[GetCarrierServicesResource]**](GetCarrierServicesResource.md)

### Authorization

[Bearer](api.md#Bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return list of services grouped by carrier |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to Model list]](api.md#documentation-for-models) [[Back to README]](api.md)

