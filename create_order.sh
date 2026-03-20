curl -s -X POST "https://api.parcel.royalmail.com/api/v1/orders" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "orderReference": "TEST-001",
        "orderDate": "2026-03-19T10:00:00Z",
        "subtotal": 10.00,
        "shippingCostCharged": 1.70,
        "total": 11.70,
        "currencyCode": "GBP",
        "recipient": {
          "address": {
            "fullName": "John Smith",
            "addressLine1": "1 Example Street",
            "city": "London",
            "postcode": "SW1A 1AA",
            "countryCode": "GB"
          },
          "emailAddress": "john.smith@example.com",
          "phoneNumber": "07700900000"
        },
        "packages": [
          {
            "weightInGrams": 100
          }
        ],
        "postageDetails": {
          "serviceCode": "OLP2"
        }
      }
    ]
  }'
