# CreateReturnResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**shipment** | [**CreateReturnResponseShipment**](CreateReturnResponseShipment.md) |  | [optional] 
**qr_code** | **str** |  | [optional] 
**label** | **str** |  | [optional] 

## Example

```python
from click_and_drop_api.models.create_return_response import CreateReturnResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReturnResponse from a JSON string
create_return_response_instance = CreateReturnResponse.from_json(json)
# print the JSON string representation of the object
print(CreateReturnResponse.to_json())

# convert the object into a dict
create_return_response_dict = create_return_response_instance.to_dict()
# create an instance of CreateReturnResponse from a dict
create_return_response_from_dict = CreateReturnResponse.from_dict(create_return_response_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


