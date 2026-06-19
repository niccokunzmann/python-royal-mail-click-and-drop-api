# Changelog

## 3.1.0

- `MockClickAndDrop.create_orders` raises `BadRequestException` when more than one order in the batch requests a label (`include_label_in_response=True`), matching the real API behaviour.

## v3.0.8

- Fix `PackageShippingOption.ships_to`.

## v3.0.7

- `OrderInfo.tracking_link` returns the Royal Mail tracking URL for the order, or `None`.

## v3.0.6

- `MockClickAndDrop.get_label` returns label with CN if `include_cn=True`.
- `MockClickAndDrop.create_orders` now includes a tracking code in case the service includes tracking.

## v3.0.5

- `ClickAndDrop.get_order` and `ClickAndDrop.get_orders` now return `OrderInfo` objects that have a `status_history` property
- The mock API supports setting the status for orders correctly.

## v3.0.4

- Add `manifest_orders(carrier_name=None)` to `AbstractClickAndDrop` — manifests all eligible orders (status `Label Generated` or `Despatched`) and applies postage
- Add `ManifestedOrders` type with a `.pdf` property that decodes the base64 manifest PDF to `bytearray`, returning `None` when no PDF is included
- Add `update_orders(order_identifiers, *, status, tracking_number, despatch_date, shipping_carrier, shipping_service)` to update one or more order fields in one call
- Add `set_order_status`, `set_order_tracking_number`, `set_order_despatch_date`, `set_order_shipping_carrier`, `set_order_shipping_service` convenience wrappers
- `MockClickAndDrop` accepts `is_oba: bool = True` constructor argument; `is_oba()` returns it directly without making API calls
- `MockClickAndDrop.get_label()` now returns the bundled `mock-label.pdf` from `click_and_drop_api.examples`
- `MockClickAndDrop.manifest_orders()` now returns the bundled `mock-manifest.pdf` as a base64-encoded response, with an incrementing manifest number
- Add `oba_full_workflow.py` example — end-to-end OBA flow: check account type, pick cheapest domestic service, create order with label, save label, manifest, set despatched
- Add `ClickAndDrop.from_env` as a shortcut to load the API from environment variables.

## v3.0.3

- Remove limit of 100 for `ClickAndDrop.create_orders`, `ClickAndDrop.get_orders`, `ClickAndDrop.delete_orders`
- Add `country_codes` property to `PackageShippingOption`

## v3.0.2

- Better formatted error message for `ClickAndDrop.test_shipping`
- Add `any_or_none` property to `ShippingDB`

## v3.0.1

- Add `view_order` example: print order details by order number or reference (`python -m click_and_drop_api.examples.view_order <id>`)
- `python -m click_and_drop_api.examples` now lists all examples dynamically from the directory

## v3.0.0

- cache `is_oba()` by api key
- Add `PackageShippingOption.max_weight_kg` property (converts `max_weight_g` to kg)

### Breaking changes

- remove Python 3.9 support

## v2.0.0

### Breaking changes

- `PackageSize` and `ShippingOption` have been removed and merged into the single
  class `PackageShippingOption`. The free-standing helper functions
  (`get_shipping_option`, `get_shipping_options_for`, `list_service_codes`,
  `list_package_size_codes`, `choose_package_size_by_weight`, `choose_by_weight`)
  have also been removed. Use the `db` object (a `ShippingDB` instance) instead.

### New features

- `PackageShippingOption` — flat dataclass merging all package format fields
  (`package_size_code`, `package_name`, `package_max_weight_g`, `depth_mm`,
  `width_mm`, `height_mm`, `max_sum_mm`) with all service fields. The effective
  `max_weight_g` is `min(package_max_weight_g, service_max_weight_g)`.
- `ShippingDB` — chainable registry: `for_package_size`, `for_service`,
  `for_oba`, `for_international`, `for_weight`, `filter`, `get`,
  `service_codes`, `package_size_codes`.
  Supports `len()`, `bool()`, iteration, indexing, and `repr()`.
- `_format_dimensions.py` — per-format physical constraints; Parcel Force
  services (`FE*`, `ND*`) automatically get 150 cm max length + 300 cm sum limit.
- `max_sum_mm` constraint on `PackageShippingOption` — validated in
  `dimensions_can_be_shipped` and `as_package_request`.
- Module-level `db = ShippingDB.default()` available from
  `click_and_drop_api.simple`.

## v1.4.1

- Move examples from `examples/` into `click_and_drop_api/examples/` — now executable as modules: `python -m click_and_drop_api.examples.view_version`
- Add `click_and_drop_api/examples/__init__.py` documenting all runnable examples
- Update `make test-examples` to use `python -m click_and_drop_api.examples.<name>`
- `create_order.py` now always uses a timestamped reference instead of `None`

## v1.4.0

- `ShippingTestResult` redesigned: fields are now `successful_addresses`, `failed_addresses`, `failed_messages` (list-based, one entry per country tested)
- `ShippingTestResult` gains properties: `is_success`, `is_failure`, `successful_countries`, `failed_countries`
- `test_shipping` now accepts a list of addresses/country codes and batches them in groups of 100 for efficiency
- Add `AbstractClickAndDrop.is_oba()` — detects OBA accounts by probing `a test order
- Add `AbstractClickAndDrop.get_countries_for_shipping()` — returns every country the API accepts for a given service code and package size
- Add `get_all_country_codes()` to `click_and_drop_api.simple.addresses`
- Add `examples/check_oba.py` — checks whether the account is an OBA account
- Add `examples/shipping_countries.py` — prints all countries a service code ships to

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
