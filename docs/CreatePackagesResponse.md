# CreatePackagesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**package_number** | **int** |  | [optional] 
**tracking_number** | **str** |  | [optional] 

## Example

```python
from click_and_drop_api.models.create_packages_response import CreatePackagesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePackagesResponse from a JSON string
create_packages_response_instance = CreatePackagesResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePackagesResponse.to_json())

# convert the object into a dict
create_packages_response_dict = create_packages_response_instance.to_dict()
# create an instance of CreatePackagesResponse from a dict
create_packages_response_from_dict = CreatePackagesResponse.from_dict(create_packages_response_dict)
```
[[Back to Model list]](./#documentation-for-models) [[Back to API list]](./#documentation-for-api-endpoints) [[Back to README]](./)


