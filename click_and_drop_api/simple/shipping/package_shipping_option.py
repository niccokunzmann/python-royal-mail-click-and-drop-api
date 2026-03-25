"""Shipping option model."""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from typing import Literal, Optional

from click_and_drop_api.models.dimensions_request import DimensionsRequest
from click_and_drop_api.models.shipment_package_request import ShipmentPackageRequest
from click_and_drop_api.simple.types import PostageDetails
from click_and_drop_api.simple.errors import InvalidWeight, InvalidDimensions

MIN_WEIGHT_IN_GRAMS = 1


@dataclass
class PackageShippingOption:
    """A shipping service bound to its package format.

    Merges all physical package constraints (dimensions, weight) with the
    full Royal Mail service details (code, enhancements, pricing) into one
    object so callers never have to juggle two separate instances.
    """

    # ── Package format ──────────────────────────────────────────────────────
    package_size_code: str  # API identifier, e.g. "letter", "smallParcel"
    package_name: str  # Human-readable, e.g. "Letter"
    package_max_weight_g: int  # Physical limit of the format in grams
    depth_mm: int
    width_mm: int
    height_mm: int
    # Royal Mail OBA parcel and Parcel Force use a combined L+W+D limit.
    max_sum_mm: Optional[int] = None

    # ── Shipping service ────────────────────────────────────────────────────
    brand: str = ""
    service: str = ""
    service_code: str = ""
    delivery_speed: str = ""
    compensation: D = D("0.00")
    gross: D = D("0.00")
    compensation_currency: str = "GBP"
    tax: D = D("0.00")
    international: bool = False

    # Enhancements
    tracked: bool = False
    email_notification: bool = False
    sms_notification: bool = False
    safeplace: bool = False
    age_verified: bool = False
    ioss: bool = False
    signed_for: bool = False
    local_collect: bool = False
    ddp: bool = False

    is_oba: bool = False
    # Per-service weight override (may be tighter than package_max_weight_g).
    service_max_weight_g: Optional[int] = None

    # ── Derived weight limit ────────────────────────────────────────────────

    @property
    def max_weight_g(self) -> int:
        """Effective weight limit: the tighter of format and service limits."""
        if self.service_max_weight_g is not None:
            return min(self.package_max_weight_g, self.service_max_weight_g)
        return self.package_max_weight_g

    # ── Convenience ─────────────────────────────────────────────────────────

    @property
    def net(self) -> D:
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
            "Signed For": self.signed_for,
            "Local Collect": self.local_collect,
            "Delivery duty paid": self.ddp,
        }
        return ", ".join(name for name, enabled in flags.items() if enabled)

    @property
    def dimensions_mm(self) -> tuple[int, int, int]:
        """(depth_mm, width_mm, height_mm) sorted largest-first."""
        return tuple(
            sorted((self.depth_mm, self.width_mm, self.height_mm), reverse=True)
        )

    # ── Validation ──────────────────────────────────────────────────────────

    def weight_can_be_shipped(self, weight_in_grams: int) -> bool:
        return MIN_WEIGHT_IN_GRAMS <= weight_in_grams <= self.max_weight_g

    def dimensions_can_be_shipped(
        self, height_in_mms: int, width_in_mms: int, depth_in_mms: int
    ) -> bool:
        dim = self.dimensions_mm
        asked = tuple(sorted((height_in_mms, width_in_mms, depth_in_mms), reverse=True))
        fits_box = (
            dim[0] >= asked[0]
            and dim[1] >= asked[1]
            and dim[2] >= asked[2]
            and all(v >= 0 for v in asked)
        )
        if not fits_box:
            return False
        if self.max_sum_mm is not None:
            return sum(asked) <= self.max_sum_mm
        return True

    def ships_to(self, country_code: str) -> bool:
        """Return whether this option is intended for *country_code* (ISO 3166-1 alpha-2).

        This is a static approximation based on the ``international`` flag: domestic
        options (``international=False``) match ``"GB"`` only; international options
        match every country except ``"GB"``.

        .. note::
            The Royal Mail API does **not** necessarily reject orders whose destination
            doesn't match this flag. Use
            ``api.get_countries_for_shipping(package_size, service_code)``
            to discover which countries the live API actually accepts.
        """
        country_code = country_code.upper()
        if len(country_code) != 2:
            raise ValueError(f"Invalid country code: {country_code!r}")
        return country_code != "GB" if self.international else country_code == "GB"

    # ── API request helpers ─────────────────────────────────────────────────

    def as_postage_details(
        self,
        send_notifications_to: Optional[
            Literal["sender", "recipient", "billing"]
        ] = None,
        **attributes,
    ) -> PostageDetails:
        return PostageDetails(
            service_code=self.service_code,
            send_notifications_to=send_notifications_to,
            **attributes,
        )

    def as_package_request(
        self,
        weight_in_grams: int,
        height_in_mms: Optional[int] = None,
        width_in_mms: Optional[int] = None,
        depth_in_mms: Optional[int] = None,
    ) -> ShipmentPackageRequest:
        """Build a :class:`ShipmentPackageRequest` validated against all limits.

        Raises:
            InvalidWeight: weight outside [1g, max_weight_g].
            InvalidDimensions: dimensions exceed this option's box / sum limit.
        """
        if not self.weight_can_be_shipped(weight_in_grams):
            raise InvalidWeight(
                f"{MIN_WEIGHT_IN_GRAMS}g to {self.max_weight_g}g allowed"
                f", got {weight_in_grams}g."
            )
        dimensions = None
        if height_in_mms or width_in_mms or depth_in_mms:
            height_in_mms, width_in_mms, depth_in_mms = sorted(
                (height_in_mms, width_in_mms, depth_in_mms), reverse=True
            )
            if not self.dimensions_can_be_shipped(
                height_in_mms, width_in_mms, depth_in_mms
            ):
                sh, sw, sl = sorted(
                    (self.height_mm, self.width_mm, self.depth_mm), reverse=True
                )
                detail = f" (sum ≤ {self.max_sum_mm} mm)" if self.max_sum_mm else ""
                raise InvalidDimensions(
                    f"{height_in_mms}×{width_in_mms}×{depth_in_mms} mm does not "
                    f"fit into {sh}×{sw}×{sl} mm{detail}."
                )
            dimensions = DimensionsRequest(
                height_in_mms=height_in_mms,
                width_in_mms=width_in_mms,
                depth_in_mms=depth_in_mms,
            )
        return ShipmentPackageRequest(
            dimensions=dimensions,
            package_format_identifier=self.package_size_code,
            weight_in_grams=weight_in_grams,
        )

    def __repr__(self):
        """A short string representation."""
        return f"{self.__class__.__name__}({self.package_size_code!r}, {self.service_code!r})"
