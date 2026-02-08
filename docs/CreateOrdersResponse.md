# CreateOrdersResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success_count** | **int** |  | [optional] 
**errors_count** | **int** |  | [optional] 
**created_orders** | [**List[CreateOrderResponse]**](CreateOrderResponse.md) |  | [optional] 
**failed_orders** | [**List[FailedOrderResponse]**](FailedOrderResponse.md) |  | [optional] 

## Example

```python
from click_and_drop_api.models.create_orders_response import CreateOrdersResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrdersResponse from a JSON string
create_orders_response_instance = CreateOrdersResponse.from_json(json)
# print the JSON string representation of the object
print(CreateOrdersResponse.to_json())

# convert the object into a dict
create_orders_response_dict = create_orders_response_instance.to_dict()
# create an instance of CreateOrdersResponse from a dict
create_orders_response_from_dict = CreateOrdersResponse.from_dict(create_orders_response_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


