# GetServicesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**services** | [**List[ServiceItem]**](ServiceItem.md) |  | [optional] 

## Example

```python
from click_and_drop_api.models.get_services_response import GetServicesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetServicesResponse from a JSON string
get_services_response_instance = GetServicesResponse.from_json(json)
# print the JSON string representation of the object
print(GetServicesResponse.to_json())

# convert the object into a dict
get_services_response_dict = get_services_response_instance.to_dict()
# create an instance of GetServicesResponse from a dict
get_services_response_from_dict = GetServicesResponse.from_dict(get_services_response_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


