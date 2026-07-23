# ManifestEligibleOrdersRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**carrier_name** | **str** | The name of the carrier you would like to manifest orders for. This is required if the account has multiple carriers or multiple postage location numbers, and must match the name configured in **Settings → Carrier settings** on the Click & Drop website. A typical value for an OBA account is `"Royal Mail OBA"`. Omit (or pass `null`) for single-carrier accounts. | [optional] 

## Example

```python
from click_and_drop_api.models.manifest_eligible_orders_request import ManifestEligibleOrdersRequest

# Single-carrier account — no carrier name needed
req = ManifestEligibleOrdersRequest()

# Multi-carrier account — carrier name must match Settings → Carrier settings
req = ManifestEligibleOrdersRequest(carrier_name="Royal Mail OBA")
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


