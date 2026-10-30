# OlpServicesResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**guidance_text** | **str** |  | [optional] 
**services** | [**List[OlpServiceOption]**](OlpServiceOption.md) |  | [optional] 

## Example

```python
from click_and_drop_api.models.olp_services_result import OlpServicesResult

# TODO update the JSON string below
json = "{}"
# create an instance of OlpServicesResult from a JSON string
olp_services_result_instance = OlpServicesResult.from_json(json)
# print the JSON string representation of the object
print(OlpServicesResult.to_json())

# convert the object into a dict
olp_services_result_dict = olp_services_result_instance.to_dict()
# create an instance of OlpServicesResult from a dict
olp_services_result_from_dict = OlpServicesResult.from_dict(olp_services_result_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


