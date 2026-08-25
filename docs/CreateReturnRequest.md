# CreateReturnRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**service** | [**ServiceCode**](ServiceCode.md) |  | 
**shipment** | [**Shipment**](Shipment.md) |  | 

## Example

```python
from click_and_drop_api.models.create_return_request import CreateReturnRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReturnRequest from a JSON string
create_return_request_instance = CreateReturnRequest.from_json(json)
# print the JSON string representation of the object
print(CreateReturnRequest.to_json())

# convert the object into a dict
create_return_request_dict = create_return_request_instance.to_dict()
# create an instance of CreateReturnRequest from a dict
create_return_request_from_dict = CreateReturnRequest.from_dict(create_return_request_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


