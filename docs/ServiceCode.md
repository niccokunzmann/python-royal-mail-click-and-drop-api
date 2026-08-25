# ServiceCode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**service_code** | **str** | Return service code. Obtain available values from GET /returns/services. | 
**service_register_code** | **str** |  | [optional] 

## Example

```python
from click_and_drop_api.models.service_code import ServiceCode

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceCode from a JSON string
service_code_instance = ServiceCode.from_json(json)
# print the JSON string representation of the object
print(ServiceCode.to_json())

# convert the object into a dict
service_code_dict = service_code_instance.to_dict()
# create an instance of ServiceCode from a dict
service_code_from_dict = ServiceCode.from_dict(service_code_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


