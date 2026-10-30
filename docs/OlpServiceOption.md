# OlpServiceOption


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**service_code** | **str** |  | [optional] 
**service_name** | **str** |  | [optional] 
**brand** | **str** |  | [optional] 
**service_level** | **str** |  | [optional] 
**package_format** | **str** |  | [optional] 
**min_weight_grams** | **int** |  | [optional] 
**max_weight_grams** | **int** |  | [optional] 
**cost** | **float** |  | [optional] 
**vat_cost** | **float** |  | [optional] 
**enhancements** | **List[str]** |  | [optional] 
**drop_off_options** | **List[str]** |  | [optional] 

## Example

```python
from click_and_drop_api.models.olp_service_option import OlpServiceOption

# TODO update the JSON string below
json = "{}"
# create an instance of OlpServiceOption from a JSON string
olp_service_option_instance = OlpServiceOption.from_json(json)
# print the JSON string representation of the object
print(OlpServiceOption.to_json())

# convert the object into a dict
olp_service_option_dict = olp_service_option_instance.to_dict()
# create an instance of OlpServiceOption from a dict
olp_service_option_from_dict = OlpServiceOption.from_dict(olp_service_option_dict)
```
[[Back to Model list]](api.md#documentation-for-models) [[Back to API list]](api.md#documentation-for-api-endpoints) [[Back to README]](api.md)


