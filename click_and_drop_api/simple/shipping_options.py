"""Shipping options for Click and Drop API."""

from __future__ import annotations
from decimal import Decimal as D
from typing import Literal, NamedTuple, Optional, Sequence
from .types import PostageDetails


class ShippingOption(NamedTuple):
    brand: str
    service: str
    service_code: str
    delivery_speed: str
    compensation: D
    gross: D
    compensation_currency: str = "GBP"
    enhancement: str = ""
    tax: D = D("0.00")

    @property
    def net(self):
        return self.gross - self.tax

    def as_postage_details(
        self,
        send_notifications_to: Optional[
            Literal["sender", "recipient", "billing"]
        ] = None,
        **attribtues,
    ) -> PostageDetails:
        """PostageDetails generated from this ShippingOption.

        Minimal attributes are set and you can modify them later.

        Parameters:
            attribtues: Additional attributes to set on the PostageDetails
        """
        return PostageDetails(
            service_code=self.service_code,
            # carrier_name=self.service,  # it seems that this is not included in the API
            send_notifications_to=send_notifications_to,
            **attribtues,
        )

    @classmethod
    def with_code(cls, service_code: str) -> ShippingOption:
        """Get a shipping option for the service code.

        Returns:
            The shipping option

        Raises:
            KeyError
        """
        return shipping_options[service_code]


shipping_options = {}


def add_shipping_option(
    brand: str,
    service: str,
    service_code: str,
    delivery_speed: str,
    compensation: D,
    compensation_currency: str,
    enhancement: str,
    tax: D,
    gross: D,
):
    """Add a shipping option to the list of available options."""
    shipping_options[service_code] = ShippingOption(
        brand=brand,
        service=service,
        service_code=service_code,
        delivery_speed=delivery_speed,
        compensation=compensation,
        compensation_currency=compensation_currency,
        enhancement=enhancement,
        tax=tax,
        gross=gross,
    )


def list_service_codes() -> list[str]:
    """All shipping option service codes."""
    return list(shipping_options.keys())


def check_service_codes(service_codes: Sequence[str]):
    """Check if all service codes are valid."""
    for service_code in service_codes:
        if service_code not in shipping_options:
            raise ValueError(
                f"Invalid service code: {service_code}. Should be one of {', '.join(list_service_codes())}"
            )


# Royal Mail 1st Class (£20 compensation)
# See details
# 	OLP1
# 24 hour (next working day)
# 	Up to £20 		£1.70 	£0.00 	£1.70
add_shipping_option(
    "Royal Mail",
    "Royal Mail 1st Class (£20 compensation)",
    "OLP1",
    "24 hour (next working day)",
    D("20.00"),
    "GBP",
    "",
    D("0.00"),
    D("1.70"),
)


# Royal Mail Signed For 1st Class (£20 compensation)
# See details
# 	OLP1SF
# 24 hour (next working day)
# 	Up to £20 		£3.60 	£0.00 	£3.60
add_shipping_option(
    "Royal Mail",
    "Royal Mail Signed For 1st Class (£20 compensation)",
    "OLP1SF",
    "24 hour (next working day)",
    D("20.00"),
    "GBP",
    "",
    D("0.00"),
    D("3.60"),
)

# Royal Mail 2nd Class (£20 compensation)
# See details
# 	OLP2
# 48 hour (2 working days)
# 	Up to £20 		£0.87 	£0.00 	£0.87
add_shipping_option(
    "Royal Mail",
    "Royal Mail 2nd Class (£20 compensation)",
    "OLP2",
    "48 hour (2 working days)",
    D("20.00"),
    "GBP",
    "",
    D("0.00"),
    D("0.87"),
)

# Royal Mail Signed For 2nd Class (£20 compensation)
# See details
# 	OLP2SF
# 48 hour (2 working days)
# 	Up to £20 		£2.77 	£0.00 	£2.77
add_shipping_option(
    "Royal Mail",
    "Royal Mail Signed For 2nd Class (£20 compensation)",
    "OLP2SF",
    "48 hour (2 working days)",
    D("20.00"),
    "GBP",
    "",
    D("0.00"),
    D("2.77"),
)

# Royal Mail Special Delivery Guaranteed by 1pm (£750 compensation)
# See details
# 	SD1OLP
# Guaranteed by 1pm next working day
# 	Up to £750 	Tracked, Email notification, SMS notification 	£8.75 	£0.00 	£8.75
add_shipping_option(
    "Royal Mail",
    "Royal Mail Special Delivery Guaranteed by 1pm (£750 compensation)",
    "SD1OLP",
    "Guaranteed by 1pm next working day",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("0.00"),
    D("8.75"),
)

# Royal Mail Special Delivery Guaranteed by 1pm (£1000 compensation)
# See details
# 	SD2OLP
# Guaranteed by 1pm next working day
# 	Up to £1000 	Tracked, Email notification, SMS notification 	£11.75 	£0.00 	£11.75
add_shipping_option(
    "Royal Mail",
    "Royal Mail Special Delivery Guaranteed by 1pm (£1000 compensation)",
    "SD2OLP",
    "Guaranteed by 1pm next working day",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("0.00"),
    D("11.75"),
)

# Royal Mail Special Delivery Guaranteed by 1pm (£2500 compensation)
# See details
# 	SD3OLP
# Guaranteed by 1pm next working day
# 	Up to £2500 	Tracked, Email notification, SMS notification 	£18.75 	£0.00 	£18.75
add_shipping_option(
    "Royal Mail",
    "Royal Mail Special Delivery Guaranteed by 1pm (£2500 compensation)",
    "SD3OLP",
    "Guaranteed by 1pm next working day",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("0.00"),
    D("18.75"),
)


# Tracked 24 (£75 compensation)
# See details
# 	TOLP24
# 24 hour (next working day)
# 	Up to £75 	Tracked, Email notification, SMS notification, Safeplace 	£3.04 	£0.61 	£3.65
add_shipping_option(
    "Royal Mail",
    "Tracked 24 (£75 compensation)",
    "TOLP24",
    "24 hour (next working day)",
    D("75.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("0.61"),
    D("3.65"),
)

# Tracked 24 with Signature (£75 compensation)
# See details
# 	TOLP24SF
# 24 hour (next working day)
# 	Up to £75 	Tracked, Email notification, SMS notification 	£4.62 	£0.93 	£5.55
add_shipping_option(
    "Royal Mail",
    "Tracked 24 with Signature (£75 compensation)",
    "TOLP24SF",
    "24 hour (next working day)",
    D("75.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("0.93"),
    D("5.55"),
)

# Tracked 48 (£75 compensation)
# See details
# 	TOLP48
# 48 hour (2 working days)
# 	Up to £75 	Tracked, Email notification, SMS notification, Safeplace 	£2.29 	£0.46 	£2.75
add_shipping_option(
    "Royal Mail",
    "Tracked 48 (£75 compensation)",
    "TOLP48",
    "48 hour (2 working days)",
    D("75.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("0.46"),
    D("2.75"),
)

# Tracked 48 with Signature (£75 compensation)
# See details
# 	TOLP48SF
# 48 hour (2 working days)
# 	Up to £75 	Tracked, Email notification, SMS notification 	£3.87 	£0.78 	£4.65
add_shipping_option(
    "Royal Mail",
    "Tracked 48 with Signature (£75 compensation)",
    "TOLP48SF",
    "48 hour (2 working days)",
    D("75.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("0.78"),
    D("4.65"),
)


# Tracked 24 with Age Verification (£75 compensation)
# See details
# 	TOLP24SFA
# 24 hour (next working day)
# 	Up to £75 	Tracked, Email notification, SMS notification, Age verified on delivery 	£6.11 	£1.22 	£7.33
add_shipping_option(
    "Royal Mail",
    "Tracked 24 with Age Verification (£75 compensation)",
    "TOLP24SFA",
    "24 hour (next working day)",
    D("75.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Age verified on delivery",
    D("1.22"),
    D("7.33"),
)


# Tracked 48 with Age Verification (£75 compensation)
# See details
# 	TOLP48SFA
# 48 hour (2 working days)
# 	Up to £75 	Tracked, Email notification, SMS notification, Age verified on delivery 	£5.36 	£1.07 	£6.43
add_shipping_option(
    "Royal Mail",
    "Tracked 48 with Age Verification (£75 compensation)",
    "TOLP48SFA",
    "48 hour (2 working days)",
    D("75.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Age verified on delivery",
    D("1.07"),
    D("6.43"),
)


########### Parcel Force


# express10 with Signature Comp 1 (£750 compensation)
# See details
# 	PFE10SF
#  Guaranteed by 10am next working day
# 	Up to £750 	Tracked, Email notification, SMS notification 	£29.37 	£5.88 	£35.25
add_shipping_option(
    "Parcel Force",
    "express10 with Signature Comp 1 (£750 compensation)",
    "PFE10SF",
    "Guaranteed by 10am next working day",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("5.88"),
    D("35.25"),
)


# express10 with Signature Comp 2 (£1000 compensation)
# See details
# 	PFE10SF
# Guaranteed by 10am next working day
# 	Up to £1000 	Tracked, Email notification, SMS notification 	£48.54 	£9.71 	£58.25
add_shipping_option(
    "Parcel Force",
    "express10 with Signature Comp 2 (£1000 compensation)",
    "PFE10SF",
    "Guaranteed by 10am next working day",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("9.71"),
    D("58.25"),
)

# express10 with Signature Comp 3 (£2500 compensation)
# See details
# 	PFE10SF
# Guaranteed by 10am next working day
# 	Up to £2500 	Tracked, Email notification, SMS notification 	£77.71 	£15.54 	£93.25
add_shipping_option(
    "Parcel Force",
    "express10 with Signature Comp 3 (£2500 compensation)",
    "PFE10SF",
    "Guaranteed by 10am next working day",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("15.54"),
    D("93.25"),
)

# express24 (£150 compensation)
# See details
# 	PFE24
# 24 hour (next working day)
# 	Up to £150 	Tracked, Email notification, SMS notification, Safeplace 	£9.92 	£1.98 	£11.90
add_shipping_option(
    "Parcel Force",
    "express24 (£150 compensation)",
    "PFE24",
    "24 hour (next working day)",
    D("150.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("1.98"),
    D("11.90"),
)

# express24 Comp 1 (£750 compensation)
# See details
# 	PFE24
# 24 hour (next working day)
# 	Up to £750 	Tracked, Email notification, SMS notification, Safeplace 	£15.75 	£3.15 	£18.90
add_shipping_option(
    "Parcel Force",
    "express24 Comp 1 (£750 compensation)",
    "PFE24",
    "24 hour (next working day)",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("3.15"),
    D("18.90"),
)

# express24 Comp 2 (£1000 compensation)
# See details
# 	PFE24
# 24 hour (next working day)
# 	Up to £1000 	Tracked, Email notification, SMS notification, Safeplace 	£34.92 	£6.98 	£41.90
add_shipping_option(
    "Parcel Force",
    "express24 Comp 2 (£1000 compensation)",
    "PFE24",
    "24 hour (next working day)",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("6.98"),
    D("41.90"),
)


# express24 Comp 3 (£2500 compensation)
# See details
# 	PFE24
# 24 hour (next working day)
# 	Up to £2500 	Tracked, Email notification, SMS notification, Safeplace 	£64.09 	£12.81 	£76.90
add_shipping_option(
    "Parcel Force",
    "express24 Comp 3 (£2500 compensation)",
    "PFE24",
    "24 hour (next working day)",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("12.81"),
    D("76.90"),
)

# express24 with Signature (£150 compensation)
# See details
# 	PFE24SF
# 24 hour (next working day)
# 	Up to £150 	Tracked, Email notification, SMS notification 	£11.17 	£2.23 	£13.40
add_shipping_option(
    "Parcel Force",
    "express24 with Signature (£150 compensation)",
    "PFE24SF",
    "24 hour (next working day)",
    D("150.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("2.23"),
    D("13.40"),
)

# express24 with Signature Comp 1 (£750 compensation)
# See details
# 	PFE24SF
# 24 hour (next working day)
# 	Up to £750 	Tracked, Email notification, SMS notification 	£17.00 	£3.40 	£20.40
add_shipping_option(
    "Parcel Force",
    "express24 with Signature Comp 1 (£750 compensation)",
    "PFE24SF",
    "24 hour (next working day)",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("3.40"),
    D("20.40"),
)

# express24 with Signature Comp 2 (£1000 compensation)
# See details
# 	PFE24SF
# 24 hour (next working day)
# 	Up to £1000 	Tracked, Email notification, SMS notification 	£36.17 	£7.23 	£43.40
add_shipping_option(
    "Parcel Force",
    "express24 with Signature Comp 2 (£1000 compensation)",
    "PFE24SF",
    "24 hour (next working day)",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("7.23"),
    D("43.40"),
)

# express24 with Signature Comp 3 (£2500 compensation)
# See details
# 	PFE24SF
# 24 hour (next working day)
# 	Up to £2500 	Tracked, Email notification, SMS notification 	£65.34 	£13.06 	£78.40
add_shipping_option(
    "Parcel Force",
    "express24 with Signature Comp 3 (£2500 compensation)",
    "PFE24SF",
    "24 hour (next working day)",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("13.06"),
    D("78.40"),
)

# express48 (£150 compensation)
# See details
# 	PFE48
# 48 hour (2 working days)
# 	Up to £150 	Tracked, Email notification, SMS notification, Safeplace 	£9.46 	£1.89 	£11.35
add_shipping_option(
    "Parcel Force",
    "express48 (£150 compensation)",
    "PFE48",
    "48 hour (2 working days)",
    D("150.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("1.89"),
    D("11.35"),
)

# express48 Comp 1 (£750 compensation)
# See details
# 	PFE48
# 48 hour (2 working days)
# 	Up to £750 	Tracked, Email notification, SMS notification, Safeplace 	£15.29 	£3.06 	£18.35
add_shipping_option(
    "Parcel Force",
    "express48 Comp 1 (£750 compensation)",
    "PFE48",
    "48 hour (2 working days)",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("3.06"),
    D("18.35"),
)

# express48 Comp 2 (£1000 compensation)
# See details
# 	PFE48
# 48 hour (2 working days)
# 	Up to £1000 	Tracked, Email notification, SMS notification, Safeplace 	£34.46 	£6.89 	£41.35
add_shipping_option(
    "Parcel Force",
    "express48 Comp 2 (£1000 compensation)",
    "PFE48",
    "48 hour (2 working days)",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("6.89"),
    D("41.35"),
)

# express48 Comp 3 (£2500 compensation)
# See details
# 	PFE48
# 48 hour (2 working days)
# 	Up to £2500 	Tracked, Email notification, SMS notification, Safeplace 	£63.63 	£12.72 	£76.35
add_shipping_option(
    "Parcel Force",
    "express48 Comp 3 (£2500 compensation)",
    "PFE48",
    "48 hour (2 working days)",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("12.72"),
    D("76.35"),
)

# express48 with Signature (£150 compensation)
# See details
# 	PFE48SF
# 48 hour (2 working days)
# 	Up to £150 	Tracked, Email notification, SMS notification 	£10.71 	£2.14 	£12.85
add_shipping_option(
    "Parcel Force",
    "express48 with Signature (£150 compensation)",
    "PFE48SF",
    "48 hour (2 working days)",
    D("150.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("2.14"),
    D("12.85"),
)

# express48 with Signature Comp 1 (£750 compensation)
# See details
# 	PFE48SF
# 48 hour (2 working days)
# 	Up to £750 	Tracked, Email notification, SMS notification 	£16.54 	£3.31 	£19.85
add_shipping_option(
    "Parcel Force",
    "express48 with Signature Comp 1 (£750 compensation)",
    "PFE48SF",
    "48 hour (2 working days)",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("3.31"),
    D("19.85"),
)

# express48 with Signature Comp 2 (£1000 compensation)
# See details
# 	PFE48SF
# 48 hour (2 working days)
# 	Up to £1000 	Tracked, Email notification, SMS notification 	£35.71 	£7.14 	£42.85
add_shipping_option(
    "Parcel Force",
    "express48 with Signature Comp 2 (£1000 compensation)",
    "PFE48SF",
    "48 hour (2 working days)",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("7.14"),
    D("42.85"),
)

# express48 with Signature Comp 3 (£2500 compensation)
# See details
# 	PFE48SF
# 48 hour (2 working days)
# 	Up to £2500 	Tracked, Email notification, SMS notification 	£64.88 	£12.97 	£77.85
add_shipping_option(
    "Parcel Force",
    "express48 with Signature Comp 3 (£2500 compensation)",
    "PFE48SF",
    "48 hour (2 working days)",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("12.97"),
    D("77.85"),
)

# expressAM (£150 compensation)
# See details
# 	PFEAM
# Guaranteed by 12pm next working day
# 	Up to £150 	Tracked, Email notification, SMS notification, Safeplace 	£13.08 	£2.62 	£15.70
add_shipping_option(
    "Parcel Force",
    "expressAM (£150 compensation)",
    "PFEAM",
    "Guaranteed by 12pm next working day",
    D("150.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("2.62"),
    D("15.70"),
)

# expressAM Comp 1 (£750 compensation)
# See details
# 	PFEAM
# Guaranteed by 12pm next working day
# 	Up to £750 	Tracked, Email notification, SMS notification, Safeplace 	£18.91 	£3.79 	£22.70
add_shipping_option(
    "Parcel Force",
    "expressAM Comp 1 (£750 compensation)",
    "PFEAM",
    "Guaranteed by 12pm next working day",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("3.79"),
    D("22.70"),
)

# expressAM Comp 2 (£1000 compensation)
# See details
# 	PFEAM
# Guaranteed by 12pm next working day
# 	Up to £1000 	Tracked, Email notification, SMS notification, Safeplace 	£38.08 	£7.62 	£45.70
add_shipping_option(
    "Parcel Force",
    "expressAM Comp 2 (£1000 compensation)",
    "PFEAM",
    "Guaranteed by 12pm next working day",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("7.62"),
    D("45.70"),
)

# expressAM Comp 3 (£2500 compensation)
# See details
# 	PFEAM
# Guaranteed by 12pm next working day
# 	Up to £2500 	Tracked, Email notification, SMS notification, Safeplace 	£67.25 	£13.45 	£80.70
add_shipping_option(
    "Parcel Force",
    "expressAM Comp 3 (£2500 compensation)",
    "PFEAM",
    "Guaranteed by 12pm next working day",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification, Safeplace",
    D("13.45"),
    D("80.70"),
)

# expressAM with Signature (£150 compensation)
# See details
# 	PFEAMSF
# Guaranteed by 12pm next working day
# 	Up to £150 	Tracked, Email notification, SMS notification 	£14.33 	£2.87 	£17.20
add_shipping_option(
    "Parcel Force",
    "expressAM with Signature (£150 compensation)",
    "PFEAMSF",
    "Guaranteed by 12pm next working day",
    D("150.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("2.87"),
    D("17.20"),
)

# expressAM with Signature Comp 1 (£750 compensation)
# See details
# 	PFEAMSF
# Guaranteed by 12pm next working day
# 	Up to £750 	Tracked, Email notification, SMS notification 	£20.16 	£4.04 	£24.20
add_shipping_option(
    "Parcel Force",
    "expressAM with Signature Comp 1 (£750 compensation)",
    "PFEAMSF",
    "Guaranteed by 12pm next working day",
    D("750.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("4.04"),
    D("24.20"),
)

# expressAM with Signature Comp 2 (£1000 compensation)
# See details
# 	PFEAMSF
# Guaranteed by 12pm next working day
# 	Up to £1000 	Tracked, Email notification, SMS notification 	£39.33 	£7.87 	£47.20
add_shipping_option(
    "Parcel Force",
    "expressAM with Signature Comp 2 (£1000 compensation)",
    "PFEAMSF",
    "Guaranteed by 12pm next working day",
    D("1000.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("7.87"),
    D("47.20"),
)

# expressAM with Signature Comp 3 (£2500 compensation)
# See details
# 	PFEAMSF
# Guaranteed by 12pm next working day
# 	Up to £2500 	Tracked, Email notification, SMS notification 	£68.50 	£13.70 	£82.20
add_shipping_option(
    "Parcel Force",
    "expressAM with Signature Comp 3 (£2500 compensation)",
    "PFEAMSF",
    "Guaranteed by 12pm next working day",
    D("2500.00"),
    "GBP",
    "Tracked, Email notification, SMS notification",
    D("13.70"),
    D("82.20"),
)


medium_parcel_force_codes = [
    key for key in shipping_options.keys() if key.startswith("PF")
]


def get_shipping_options(*options: str) -> list[ShippingOption]:
    """Return the shipping options with the codes."""
    return [shipping_options[code] for code in options]


__all__ = [
    "shipping_options",
    "get_shipping_options",
    "medium_parcel_force_codes",
    "ShippingOption",
    "list_service_codes",
]
