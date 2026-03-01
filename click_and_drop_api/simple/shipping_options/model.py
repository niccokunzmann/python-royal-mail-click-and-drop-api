"""Shipping option model."""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from typing import Literal, Optional
from click_and_drop_api.simple.types import PostageDetails


@dataclass
class ShippingOption:
    package_size: str
    brand: str
    service: str
    service_code: str
    delivery_speed: str
    compensation: D
    gross: D
    compensation_currency: str = "GBP"
    tax: D = D("0.00")
    international: bool = False
    tracked: bool = False
    email_notification: bool = False
    sms_notification: bool = False
    safeplace: bool = False
    age_verified: bool = False
    ioss: bool = False

    @property
    def net(self):
        return self.gross - self.tax

    @property
    def enhancement(self) -> str:
        flags = {
            "Tracked": self.tracked,
            "Email notification": self.email_notification,
            "SMS notification": self.sms_notification,
            "Safeplace": self.safeplace,
            "Age verified on delivery": self.age_verified,
            "IOSS": self.ioss,
        }
        return ", ".join(name for name, enabled in flags.items() if enabled)

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

    def ships_to(self, country_code: str) -> bool:
        """Check wether this shipping option can ship to the given country code.

        Country codes must be in ISO 3166-1 alpha-2 format.
        """
        country_code == country_code.upper()
        if len(country_code) != 2:
            raise ValueError(f"Invalid country code: {country_code}")
        if self.international:
            return country_code != "GB"
        return country_code == "GB"
