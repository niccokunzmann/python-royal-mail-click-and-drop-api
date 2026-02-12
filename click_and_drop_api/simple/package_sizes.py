"""Packages sizes for Click and Drop API."""

from __future__ import annotations
from typing import Literal, NamedTuple, Optional

from click_and_drop_api.models.dimensions_request import DimensionsRequest
from click_and_drop_api.models.shipment_package_request import ShipmentPackageRequest
from .shipping_options import (
    get_shipping_options,
    ShippingOption,
    medium_parcel_force_codes,
)
from .errors import InvalidWeight, InvalidDimensions

MAX_WEIGHT_IN_GRAMS = 30000
MIN_WEIGHT_IN_GRAMS = 1


class PackageSize(NamedTuple):
    """Choosing a package size.

    Letter
        Max weight:100g
        Max length:24cm
        Max width:16.5cm
        Max depth:0.5cm

    Large Letter
        Max weight:1kg
        Max length:35.3cm
        Max width:25cm
        Max depth:2.5cm

    Small Parcel
        Max weight:2kg
        Max length:45cm
        Max width:35cm
        Max depth:16cm

    Medium Parcel
        Max weight:20kg
        Max length:61cm
        Max width:46cm
        Max depth:46cm

    Large Parcel
        Max weight:30kg
        Max length:150cm
        Max size:depth + girth must be no more than 300cm

    """

    code: Literal[
        "undefined",
        "letter",
        "largeLetter",
        "smallParcel",
        "mediumParcel",
        "largeParcel",
        "parcel",
        "documents",
    ]
    name: str
    weight_grams: int
    depth_mm: int
    width_mm: int
    height_mm: int
    shipping_options: list[ShippingOption]

    @property
    def length_mm(self) -> int:
        """The same as the depth."""
        return self.depth_mm

    @property
    def dimensions_mm(self) -> tuple[int, int, int]:
        """The dimensions in mm.

        Returns:
            (depth_mm, width_mm, height_mm) where depth_mm >= width_mm >= height_mm
        """
        return tuple(
            sorted((self.depth_mm, self.width_mm, self.height_mm), reverse=True)
        )

    def get_shipping_option(self, code: str) -> Optional[ShippingOption]:
        """Return a shipping option with the code if it is available for this package size."""
        for shipping_option in self.shipping_options:
            if shipping_option.service_code == code:
                return shipping_option
        return None

    def get_shipping_options_in(
        self,
        selected_shipping_options: list[str],
    ) -> list[ShippingOption]:
        """Return the shipping options that also appear in selected_shipping_options.

        Parameters:
            selected_shipping_options: The shipping option codes to choose from

        Returns:
            The shipping options that can be used for this package and are also in selected_shipping_options
        """
        return [
            shipping_option
            for shipping_option in self.shipping_options
            if shipping_option.service_code in selected_shipping_options
        ]

    def with_shipping_limited_to(
        self, selected_shipping_options: list[str]
    ) -> PackageSize:
        """Return a copy with limited options for shipping."""
        return PackageSize(
            code=self.code,
            name=self.name,
            weight_grams=self.weight_grams,
            depth_mm=self.depth_mm,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            shipping_options=self.get_shipping_options_in(selected_shipping_options),
        )

    @classmethod
    def get(cls, code: str) -> PackageSize:
        """Get a package size by code.

        Returns:
            PackageSize

        Raises:
            ValueError
        """
        return get_package_size(code)

    def dimensions_can_be_shipped(
        self, height_in_mms: int, width_in_mms: int, depth_in_mms: int
    ):
        """Can the dimensions be shipped."""
        # TODO: This needs to be changed for largeParcel
        dim = self.dimensions_mm
        asked = tuple(sorted((height_in_mms, width_in_mms, depth_in_mms), reverse=True))
        return (
            dim[0] >= asked[0]
            and dim[1] >= asked[1]
            and dim[2] >= asked[2]
            and height_in_mms >= 0
            and width_in_mms >= 0
            and depth_in_mms >= 0
        )

    def weight_can_be_shipped(self, weight_in_grams: int):
        """Can the weight be shipped.

        The APIrequires a minimum weight of 1g.
        And a maximum weight of 30000g (30kg).
        """
        return (
            MIN_WEIGHT_IN_GRAMS <= weight_in_grams
            and weight_in_grams <= self.weight_grams
        )

    def as_package_request(
        self,
        weight_in_grams: int,
        height_in_mms: Optional[int] = None,
        width_in_mms: Optional[int] = None,
        depth_in_mms: Optional[int] = None,
    ) -> ShipmentPackageRequest:
        """Return the package size as a ShipmentPackageRequest.

        You can set more attributes of this object.

        Parameters:
            weight_in_grams: The weight in grams
            height_in_mms: The height in mm
            width_in_mms: The width in mm
            depth_in_mms: The depth in mm

        Returns:
            The package request

        Raises:
            ValueError: If the weight is too heavy or the dimensions are too big.
        """
        if not self.weight_can_be_shipped(weight_in_grams):
            raise InvalidWeight(
                f"{MIN_WEIGHT_IN_GRAMS}g to {self.weight_grams}g allowed, got {weight_in_grams}g."
            )
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
                raise InvalidDimensions(
                    f"{height_in_mms}mm x {width_in_mms}mm x {depth_in_mms}mm does not fit into {sh}mm x {sw}mm x {sl}mm."
                )
            dimensions = DimensionsRequest(
                height_in_mms=height_in_mms,
                width_in_mms=width_in_mms,
                depth_in_mms=depth_in_mms,
            )
        else:
            dimensions = None
        return ShipmentPackageRequest(
            dimensions=dimensions,
            package_format_identifier=self.code,
            weight_in_grams=weight_in_grams,
        )


packages_sizes = [
    PackageSize(
        "letter",
        "Letter",
        100,
        240,
        165,
        5,
        get_shipping_options(
            "OLP1", "OLP1SF", "OLP2", "OLP2SF", "SD1OLP", "SD2OLP", "SD3OLP"
        ),
    ),
    PackageSize(
        "largeLetter",
        "Large letter",
        1000,
        353,
        250,
        25,
        get_shipping_options(
            "OLP1",
            "OLP1SF",
            "OLP2",
            "OLP2SF",
            "SD1OLP",
            "SD2OLP",
            "SD3OLP",
            "TOLP24",
            "TOLP24SF",
            "TOLP48",
            "TOLP48SF",
        ),
    ),
    PackageSize(
        "smallParcel",
        "Small parcel",
        2000,
        450,
        350,
        160,
        get_shipping_options(
            "OLP1",
            "OLP1SF",
            "OLP2",
            "OLP2SF",
            "SD1OLP",
            "SD2OLP",
            "SD3OLP",
            "TOLP24",
            "TOLP24SF",
            "TOLP24SFA",
            "TOLP48",
            "TOLP48SF",
            "TOLP48SFA",
        ),
    ),
    PackageSize(
        "mediumParcel",
        "Medium parcel",
        20000,
        610,
        460,
        460,
        get_shipping_options(
            "OLP1",
            "OLP1SF",
            "OLP2",
            "OLP2SF",
            "SD1OLP",
            "SD2OLP",
            "SD3OLP",
            "TOLP24",
            "TOLP24SF",
            "TOLP24SFA",
            "TOLP48",
            "TOLP48SF",
            "TOLP48SFA",
            *medium_parcel_force_codes,
        ),
    ),
    PackageSize(
        "largeParcel", "Large parcel", 30000, 1500, 3000, 3000, []
    ),  # TODO: options
]

# TODO: Missing "parcel" and "documents"


def choose_package_size_by_weight(
    weight_grams: int, possible_packages_codes: Optional[list[str]] = None
) -> Optional[PackageSize]:
    """Return the best package size based on weight in grams.

    Parameters:
        weight_grams: The weight in grams
        possible_packages_sizes: The package sizes to choose from or None to use all available sizes.

    Returns:
        The best package size.
        If the weight is too heavy, return None.
    """
    if possible_packages_codes is None:
        possible_packages_sizes = packages_sizes
    else:
        possible_packages_sizes = get_package_sizes(possible_packages_codes)
    for package_size in possible_packages_sizes:
        if weight_grams <= package_size.weight_grams:
            return package_size


def list_package_sizes() -> list[str]:
    """List all package sizes."""
    return [package_size.code for package_size in packages_sizes]


def get_package_size(code: str) -> PackageSize:
    """Get a package size by code.

    Returns:
        PackageSize

    Raises:
        ValueError
    """
    for package_size in packages_sizes:
        if package_size.code == code:
            return package_size
    raise ValueError(
        f"Unknown package size: {code!r}. Got {', '.join(list_package_sizes())}"
    )


def get_package_sizes(codes: list[str]) -> list[PackageSize]:
    """Return the package sizes with the given codes."""
    return [get_package_size(code) for code in codes]


__all__ = [
    "PackageSize",
    "packages_sizes",
    "get_package_size",
    "choose_package_size_by_weight",
    "list_package_sizes",
    "get_package_sizes",
    "MAX_WEIGHT_IN_GRAMS",
    "MIN_WEIGHT_IN_GRAMS",
]
