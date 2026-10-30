# GetCarrierServicesResource


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**carrier_guid** | **UUID** |  | 
**carrier_name** | **str** |  | 
**services** | [**List[GetServiceResource]**](GetServiceResource.md) |  | 

## Example

```python
from click_and_drop_api.models.get_carrier_services_resource import GetCarrierServicesResource

# TODO update the JSON string below
json = "{}"
# create an instance of GetCarrierServicesResource from a JSON string
get_carrier_services_resource_instance = GetCarrierServicesResource.from_json(json)
# print the JSON string representation of the object
print(GetCarrierServicesResource.to_json())

# convert the object into a dict
get_carrier_services_resource_dict = get_carrier_services_resource_instance.to_dict()
# create an instance of GetCarrierServicesResource from a dict
get_carrier_services_resource_from_dict = GetCarrierServicesResource.from_dict(get_carrier_services_resource_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


