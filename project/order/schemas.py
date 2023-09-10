from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from order import serializers

# EXAMPLES

ORDER_POST_EXAMPLES = [
    OpenApiExample(
        request_only=True,
        name="success with cash payment",
        value={
            "first_name": "string",
            "last_name": "string",
            "phone_number": "+380XXXXXXXXX",
            "city": "string",
            "address": "string",
            "items": [
                {
                    "product": 1,
                    "quantity": 2
                }
            ],
            "payment_mode": "cash"
        },
    ),
    OpenApiExample(
        request_only=True,
        name="success with card payment",
        value={
            "first_name": "string",
            "last_name": "string",
            "phone_number": "+380XXXXXXXXX",
            "city": "string",
            "address": "string",
            "items": [
                {
                    "product": 1,
                    "quantity": 2
                }
            ],
            "payment_mode": "cash",
            "card": "4242424242424242",
            "card_exp_month": "03",
            "card_exp_year": "22",
            "card_cvv": "123"
        },
    ),
]

# RESPONSES

ORDER_POST_RESPONSES = {
    201: {
        'properties': {'order_number': {'type': 'integer'}}
    },
    400: OpenApiResponse(description='Bad request (something invalid)'),
}

ORDER_DETAIL_RESPONSES = {
    200: serializers.OrderDetailSerializer(),
    404: OpenApiResponse(description='Not found'),
}
