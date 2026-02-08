# ManifestEligibleOrdersRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**carrier_name** | **str** | The name of the carrier you would like to manifest orders for. This is required if the account has multiple carriers or multiple postage location numbers, and must match the name configured in the carrier settings within the main website.  | [optional] 

## Example

```python
from click_and_drop_api.models.manifest_eligible_orders_request import ManifestEligibleOrdersRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ManifestEligibleOrdersRequest from a JSON string
manifest_eligible_orders_request_instance = ManifestEligibleOrdersRequest.from_json(json)
# print the JSON string representation of the object
print ManifestEligibleOrdersRequest.to_json()

# convert the object into a dict
manifest_eligible_orders_request_dict = manifest_eligible_orders_request_instance.to_dict()
# create an instance of ManifestEligibleOrdersRequest from a dict
manifest_eligible_orders_request_from_dict = ManifestEligibleOrdersRequest.from_dict(manifest_eligible_orders_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


