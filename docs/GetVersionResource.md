# GetVersionResource


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commit** | **str** |  | [optional] 
**build** | **str** |  | [optional] 
**release** | **str** |  | [optional] 
**release_date** | **datetime** |  | 

## Example

```python
from click_and_drop_api.models.get_version_resource import GetVersionResource

# TODO update the JSON string below
json = "{}"
# create an instance of GetVersionResource from a JSON string
get_version_resource_instance = GetVersionResource.from_json(json)
# print the JSON string representation of the object
print(GetVersionResource.to_json())

# convert the object into a dict
get_version_resource_dict = get_version_resource_instance.to_dict()
# create an instance of GetVersionResource from a dict
get_version_resource_from_dict = GetVersionResource.from_dict(get_version_resource_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


