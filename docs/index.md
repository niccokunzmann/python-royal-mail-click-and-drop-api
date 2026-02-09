# Royal Mail's Click & Drop API for Python

The Royal Mail Click & Drop API allows you to import your orders, retrieve your orders and generate labels.
This package is an inofficial auto-generated Python client for this API.

Read about the Click & Drop API:

- [Royal Mail Help Centre](https://help.parcel.royalmail.com/hc/en-gb/sections/360003305257-Click-Drop-API)
- [Click & Drop API Specification](https://api.parcel.royalmail.com/)

## Installation

```bash
pip install click_and_drop_api
```

## API Reference

This package has extensive documentation for the API Reference, which can be found [here](api.md).

## API Key

You need an API key to use the Click & Drop API.
You can get this key here:

1. Register an account at [parcel.royalmail.com](https://parcel.royalmail.com/)
2. Login at [auth.parcel.royalmail.com](https://auth.parcel.royalmail.com/)
3. Go to `Settings` → `Integrations` → `Add a new integration` → `Click & Drop API`
4. Fill out the details and save/update them.
5. Copy the `Click & Drop API authorisation key`

```bash
export API_KEY="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
```

The API key will be used on the examples below to authenticate the requests.

## Examples

The script below uses the API to retrieve the version of the Click & Drop API.

```python
--8<-- "docs/examples/view_version.py"
```
