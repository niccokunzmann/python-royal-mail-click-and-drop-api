# CreateReturnResponseShipment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tracking_number** | **str** |  | [optional] 
**unique_item_id** | **str** |  | [optional] 

## Example

```python
from click_and_drop_api.models.create_return_response_shipment import CreateReturnResponseShipment

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReturnResponseShipment from a JSON string
create_return_response_shipment_instance = CreateReturnResponseShipment.from_json(json)
# print the JSON string representation of the object
print(CreateReturnResponseShipment.to_json())

# convert the object into a dict
create_return_response_shipment_dict = create_return_response_shipment_instance.to_dict()
# create an instance of CreateReturnResponseShipment from a dict
create_return_response_shipment_from_dict = CreateReturnResponseShipment.from_dict(create_return_response_shipment_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


