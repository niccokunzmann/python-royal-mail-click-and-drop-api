# Changelog

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
