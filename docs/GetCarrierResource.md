# GetCarrierResource


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**carrier_guid** | **UUID** |  | 
**carrier_name** | **str** |  | 
**carrier_status** | **str** |  | [optional] 
**carrier_type** | **str** |  | [optional] 

## Example

```python
from click_and_drop_api.models.get_carrier_resource import GetCarrierResource

# TODO update the JSON string below
json = "{}"
# create an instance of GetCarrierResource from a JSON string
get_carrier_resource_instance = GetCarrierResource.from_json(json)
# print the JSON string representation of the object
print(GetCarrierResource.to_json())

# convert the object into a dict
get_carrier_resource_dict = get_carrier_resource_instance.to_dict()
# create an instance of GetCarrierResource from a dict
get_carrier_resource_from_dict = GetCarrierResource.from_dict(get_carrier_resource_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


