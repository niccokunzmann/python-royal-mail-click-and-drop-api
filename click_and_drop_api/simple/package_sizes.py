"""Packages sizes for Click and Drop API."""

from __future__ import annotations
from typing import NamedTuple, Optional
from .shipping_options import (
    get_shipping_options,
    ShippingOption,
    medium_parcel_force_codes,
)


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
        Max size:Length + girth must be no more than 300cm

    """

    code: str
    name: str
    weight_grams: int
    length_mm: int
    width_mm: int
    height_mm: int
    shipping_options: list[ShippingOption]

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
            length_mm=self.length_mm,
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
]
