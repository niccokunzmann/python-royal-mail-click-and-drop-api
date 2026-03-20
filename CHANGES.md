# Changelog

## v1.3.0

- Add `AbstractClickAndDrop` ABC with shared interface for `ClickAndDrop` and `MockClickAndDrop`
- Add `MockClickAndDrop` — in-memory drop-in replacement for unit tests
- Concrete `create_order`, `get_order`, `delete_order` helpers on the ABC (delegate to plural abstract methods)
- Add `ShippingTestResult` named tuple and `AbstractClickAndDrop.test_shipping()` — creates and immediately deletes a test order against the API
- `test_shipping` accepts a destination as an `Address` instance or an ISO 3166-1 alpha-2 country code string
- Add `click_and_drop_api.simple.addresses` — sample valid addresses for all 249 ISO 3166-1 countries, accessible via `ADDRESSES["DE"]` or `get_address("DE")`
- Add OBA shipping options: `letter`, `large_letter`, `parcel`, `documents` modules now include OBA service codes parsed from txt files
- Add `parcel` and `documents` `PackageSize` instances to `package_sizes`
- Add `ShippingOption.is_oba` flag and `max_weight_g` field
- Add enhancement flags: `signed_for`, `local_collect`, `ddp`
- Add `ServiceConstraint` dataclass and `SERVICE_CONSTRAINTS` dict to `parcel` module — per-service-code physical limits (weight + dimensions) for all OBA parcel service codes
- Add `SERVICE_MAX_WEIGHT_G` to `parcel` module — per-service-code weight limits verified against the live API via `scripts/test_parcel_orders.py`
- Add `scripts/test_parcel_orders.py` — creates test orders for each parcel type and reports 3 kg capability per service code

## v1.2.1

- fix: include the shipping option files.

## v1.2.0 (yanked)

- Remove add_shipping_option and shipping_options from the API
- record international sending
- parse shipping options from files with content copied from the website where you apply postage
- Add `ShippingOption.ships_to` to check if the shipping option can ship to a country

## v1.1.1

- Document how to create an OBA
- Add label generation example
- Make order creation easier and add label request example
- add `ClickAndDrop.get_label()`

## v1.1.0

- Add better typing for `PackageSize`.
- Add methods to check for weight and size in `PackageSize`
- Add conversion methods to make creating a API request easier.
- Use dependency groups
- Add more information to the example order creation

## v1.0.7

- Add `PackageSize.get()`
- Correct codes of package sizes (large-letter -> largeLetter, small-parcel -> smallParcel, etc.)

## v1.0.6

- Allow limiting the list of shipping options when calculating by weight.

## v1.0.5

- add `click_and_drop_api.simple.package_sizes.PackageSize.with_shipping_limited_to`

## v1.0.4

- allow checking for service codes

## v1.0.3

- add packages and shipping info

## v1.0.2

- Sanitize and check key in `click_and_drop_api.simple.ClickAndDrop`

## v1.0.1

- Correct link from PyPI to GitHub

## v1.0.0

- Initial release
- Support for the Click and Drop API
- Auto-generated Python client
- Add tests
- Add `click-and-drop-api` to PyPI
- Add `click_and_drop_api.simple` with a simplified interface.
