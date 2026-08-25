# ServiceItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**carrier_guid** | **UUID** |  | [optional] 
**carrier_service_guid** | **UUID** |  | [optional] 
**service_name** | **str** |  | [optional] 
**service_code** | **str** |  | [optional] 

## Example

```python
from click_and_drop_api.models.service_item import ServiceItem

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceItem from a JSON string
service_item_instance = ServiceItem.from_json(json)
# print the JSON string representation of the object
print(ServiceItem.to_json())

# convert the object into a dict
service_item_dict = service_item_instance.to_dict()
# create an instance of ServiceItem from a dict
service_item_from_dict = ServiceItem.from_dict(service_item_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


