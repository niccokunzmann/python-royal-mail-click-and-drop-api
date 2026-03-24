from click_and_drop_api.simple import Address


from typing import NamedTuple


class ShippingTestResult(NamedTuple):
    """Result of a live API shipping test."""

    successful_addresses: list[Address]
    failed_addresses: list[Address]
    failed_messages: list[str]

    @property
    def is_success(self) -> bool:
        """Whether all addresses succeeded.

        Note: If you have several countries to test, this will be ``True`` if
        *any* country succeeds.
        """
        return bool(self.successful_addresses)

    @property
    def is_failure(self) -> bool:
        """Whether any addresses failed.

        Note: If you have several countries to test, this will be ``True`` if
        *any* country failes.
        """
        return bool(self.failed_addresses)

    @property
    def failed_countries(self) -> list[str]:
        """List of ISO 3166-1 alpha-2 country codes that failed."""
        return [a.country_code for a in self.failed_addresses]

    @property
    def successful_countries(self) -> list[str]:
        """List of ISO 3166-1 alpha-2 country codes that succeeded."""
        return [a.country_code for a in self.successful_addresses]

    @property
    def message(self) -> str:
        return "\n".join(self.failed_messages)
