"""Package sizes and shipping option lookup for the Click & Drop API."""

from __future__ import annotations
from typing import Optional

from .package_shipping_option import PackageShippingOption
from .. import shipping


class ShippingDB:
    """Registry of all available :class:`PackageShippingOption` instances.

    Acts as the single source of truth for shipping options. Supports lookup
    by package size, service code, weight, and combinations thereof.

    Usage::

        db = ShippingDB.default()
        option = db.for_package("letter").for_service("OLP2").first
        options = db.for_package("smallParcel")
        best = db.for_weight(500)
    """

    def __init__(self, options: list[PackageShippingOption]) -> None:
        self._options = options

    # ── Construction ─────────────────────────────────────────────────────────

    @classmethod
    def default(cls) -> ShippingDB:
        """Return the DB populated with all built-in shipping options."""
        return cls(shipping._get_all_shipping_options())

    # ── Lookup ────────────────────────────────────────────────────────────────

    def copy(self) -> ShippingDB:
        """All options as a new ShippingDB."""
        return ShippingDB(list(self._options))

    def for_package_size(self, package_size_code: str) -> ShippingDB:
        """All options for a given package format (e.g. ``"letter"``)."""
        return ShippingDB(
            [o for o in self._options if o.package_size_code == package_size_code]
        )

    def for_service(self, service_code: str) -> ShippingDB:
        """All options (across all package sizes) with *service_code*."""
        return ShippingDB([o for o in self._options if o.service_code == service_code])

    def for_oba(self, is_oba: bool = True) -> ShippingDB:
        """Filter by OBA flag."""
        return ShippingDB([o for o in self._options if o.is_oba == is_oba])

    def for_international(self, international: bool = True) -> ShippingDB:
        """Filter by international flag."""
        return ShippingDB(
            [o for o in self._options if o.international == international]
        )

    def for_weight(self, weight_grams: int) -> ShippingDB:
        """All options whose ``max_weight_g`` covers *weight_grams*."""
        return ShippingDB(
            [o for o in self._options if o.weight_can_be_shipped(weight_grams)]
        )

    def filter(
        self,
        *,
        package_size_code: str | None = None,
        service_code: str | None = None,
        weight_grams: int | None = None,
        is_oba: bool | None = None,
        international: bool | None = None,
    ) -> ShippingDB:
        """Filter the database.

        Parameters:
            package_size_code: Filter by package format (e.g. ``"letter"``).
            service_code: Filter by service code (e.g. ``"OLP1"``).
            weight_grams: Filter by weight (in grams).
            is_oba: Filter by OBA flag.
            international: Filter by international flag.
        """
        db = self
        if package_size_code is not None:
            db = db.for_package_size(package_size_code)
        if service_code is not None:
            db = db.for_service(service_code)
        if weight_grams is not None:
            db = db.for_weight(weight_grams)
        if is_oba is not None:
            db = db.for_oba(is_oba)
        if international is not None:
            db = db.for_international(international)
        return db

    def service_codes(self) -> list[str]:
        """All service codes (e.g. ``"OLP1"``)."""
        return list({o.service_code for o in self._options})

    def package_size_codes(self) -> list[str]:
        """All package formats (e.g. ``"letter"``)."""
        return list({o.package_size_code for o in self._options})

    def __len__(self) -> int:
        """Number of options in the DB."""
        return len(self._options)

    def __bool__(self) -> bool:
        """Whether the DB is non-empty."""
        return bool(self._options)

    def __iter__(self):
        """Iterate over all options in the DB."""
        return iter(self._options)

    def __repr__(self) -> str:
        """The DB as a string."""
        return f"{self.__class__.__name__}({self._options!r})"

    @property
    def any(self) -> PackageShippingOption:
        """Any option in the DB.

        Raises:
            IndexError: if the DB is empty.
        """
        return self._options[0]

    @property
    def any_or_none(self) -> Optional[PackageShippingOption]:
        """Any option in the DB, or ``None`` if the DB is empty."""
        return self._options[0] if self._options else None

    def __getitem__(self, key: int):
        return self._options[key]

    def get(
        self, package_size_code: str, service_code: str
    ) -> Optional[PackageShippingOption]:
        """Get any option with package format and service code."""
        try:
            return (
                self.for_package_size(package_size_code).for_service(service_code).any
            )
        except IndexError:
            return None


db = ShippingDB.default()

__all__ = [
    "ShippingDB",
    "PackageShippingOption",
    "db",
]
