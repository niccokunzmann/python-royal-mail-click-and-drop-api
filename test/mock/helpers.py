from datetime import datetime, timezone

from click_and_drop_api.simple.types import Address, CreateOrder, RecipientDetails


def make_order(reference: str = "test-ref-001") -> CreateOrder:
    return CreateOrder(
        order_reference=reference,
        order_date=datetime.now(timezone.utc),
        subtotal=10.00,
        shipping_cost_charged=0.00,
        total=10.00,
        currency_code="GBP",
        recipient=RecipientDetails(
            address=Address(
                full_name="Test User",
                address_line1="1 Test Street",
                city="London",
                postcode="SW1A 1AA",
                country_code="GB",
            )
        ),
    )
