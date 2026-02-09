# Royal Mail's Click & Drop API for Python

The Royal Mail Click & Drop API allows you to import your orders, retrieve your orders and generate labels.
This package is an inofficial auto-generated Python client for this API.

Read about the Click & Drop API:

- [Royal Mail Help Centre](https://help.parcel.royalmail.com/hc/en-gb/sections/360003305257-Click-Drop-API)
- [Click & Drop API Specification](https://api.parcel.royalmail.com/)

Links for this package:

- [Source Code](https://github.com/niccokunzmann/python-royal-mail-click-and-drop-api)
- [Documentation Website](https://niccokunzmann.github.io/python-royal-mail-click-and-drop-api/)
- [PyPI Package](https://pypi.org/project/click-and-drop-api/)
- [LICENSE GPL-3.0 or later](LICENSE.txt)

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

This sections guides you through some examples.
Export the `API_KEY` of your account to run the examples.
The examples use the simple API that is based on the generated API and reduces the amount of code.

## Retrieve the version

[Version API Documentation](https://api.parcel.royalmail.com/#tag/Version)

Retrieving the version is useful to understand if you can use the API without authentication.

```python
--8<-- "examples/view_version.py"
```

Output:

```text
--8<-- "examples/view_version.py.out"
```

## View specific orders

[Orders API Documentation](https://api.parcel.royalmail.com/#tag/Orders)

The image below shows orders that were created as examples.

![Example orders for the script to retrieve](img/orders.png)

The script below retrieves information about these orders, by id (`int`) and by reference (`str`).

```python
--8<-- "examples/view_specific_orders.py"
```

Output:

```text
--8<-- "examples/view_specific_orders.py.out"
```

## Create and delete orders

[Orders API Documentation](https://api.parcel.royalmail.com/#tag/Orders)

The script below creates a new order and then deletes it.

```python
--8<-- "examples/create_order.py"
```

Output:

```text
--8<-- "examples/create_order.py.out"
```
