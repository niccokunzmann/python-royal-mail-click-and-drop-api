class InvalidWeight(ValueError):
    """The weight cannot be shipped by this package size."""


class InvalidDimensions(ValueError):
    """The dimensions cannot be shipped by this package size."""


__all__ = [
    "InvalidWeight",
    "InvalidDimensions",
]
