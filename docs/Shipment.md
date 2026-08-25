# Shipment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**shipping_address** | [**Address**](Address.md) |  | 
**return_address** | [**Address**](Address.md) |  | 
**customer_reference** | [**CustomerReference**](CustomerReference.md) |  | [optional] 

## Example

```python
from click_and_drop_api.models.shipment import Shipment

# TODO update the JSON string below
json = "{}"
# create an instance of Shipment from a JSON string
shipment_instance = Shipment.from_json(json)
# print the JSON string representation of the object
print(Shipment.to_json())

# convert the object into a dict
shipment_dict = shipment_instance.to_dict()
# create an instance of Shipment from a dict
shipment_from_dict = Shipment.from_dict(shipment_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


