# Address


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | [optional] 
**first_name** | **str** |  | 
**last_name** | **str** |  | 
**company_name** | **str** |  | [optional] 
**address_line1** | **str** |  | 
**address_line2** | **str** |  | [optional] 
**address_line3** | **str** |  | [optional] 
**city** | **str** |  | 
**county** | **str** |  | [optional] 
**postcode** | **str** |  | 
**country** | **str** |  | 
**country_iso_code** | **str** | ISO 3166-1 alpha-3 country code (e.g. GBR, USA) | 

## Example

```python
from click_and_drop_api.models.address import Address

# TODO update the JSON string below
json = "{}"
# create an instance of Address from a JSON string
address_instance = Address.from_json(json)
# print the JSON string representation of the object
print(Address.to_json())

# convert the object into a dict
address_dict = address_instance.to_dict()
# create an instance of Address from a dict
address_from_dict = Address.from_dict(address_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


