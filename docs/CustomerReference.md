# CustomerReference


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reference** | **str** |  | 

## Example

```python
from click_and_drop_api.models.customer_reference import CustomerReference

# TODO update the JSON string below
json = "{}"
# create an instance of CustomerReference from a JSON string
customer_reference_instance = CustomerReference.from_json(json)
# print the JSON string representation of the object
print(CustomerReference.to_json())

# convert the object into a dict
customer_reference_dict = customer_reference_instance.to_dict()
# create an instance of CustomerReference from a dict
customer_reference_from_dict = CustomerReference.from_dict(customer_reference_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


