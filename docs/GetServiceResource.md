# GetServiceResource


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**carrier_service_guid** | **UUID** |  | 
**service_name** | **str** |  | 
**service_code** | **str** |  | 

## Example

```python
from click_and_drop_api.models.get_service_resource import GetServiceResource

# TODO update the JSON string below
json = "{}"
# create an instance of GetServiceResource from a JSON string
get_service_resource_instance = GetServiceResource.from_json(json)
# print the JSON string representation of the object
print(GetServiceResource.to_json())

# convert the object into a dict
get_service_resource_dict = get_service_resource_instance.to_dict()
# create an instance of GetServiceResource from a dict
get_service_resource_from_dict = GetServiceResource.from_dict(get_service_resource_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


