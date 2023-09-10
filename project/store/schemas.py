from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, inline_serializer

from store.serializers import ProductOptionSerializer, ProductCreateSerializer, ProductDetailSerializer

# EXAMPLES

CATEGORY_EXAMPLES = [
    OpenApiExample(
        name="categories example",
        value={
            "name": "string",
            "slug": "string",
            "children": [
                {
                    "name": "string",
                    "slug": "string",
                    "children": []
                }
            ]
        }
    )
]

PRODUCT_LIST_QUERY_PARAM_EXAMPLES = [
    OpenApiParameter(
        name="price_min",
        type=OpenApiTypes.DECIMAL,
        location=OpenApiParameter.QUERY,
        description='Products with a minimum price',
    ),
    OpenApiParameter(
        name="price_max",
        type=OpenApiTypes.DECIMAL,
        location=OpenApiParameter.QUERY,
        description='Products with a maximum price',
    ),
    OpenApiParameter(
        name="q",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='Search name of product',
    ),
    OpenApiParameter(
        name="value",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='Filtering products by value_id',
        examples=[
            OpenApiExample(
                name="Query Parameter Example",
                value="29,30,32",
            ),
        ],
    ),
    OpenApiParameter(
        name="o",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        many=True, enum=['-price', 'price'],
        description='Sorting products by increasing or decreasing price',
    ),
]

# RESPONSES

response_404 = OpenApiResponse(description='Not found')
properties_detail = {'detail': {'type': 'string'}}

PRODUCT_POST_RESPONSES = {
    201: ProductCreateSerializer(),
    400: OpenApiResponse(description='Bad request (something invalid)')
}

PRODUCT_DETAIL_RESPONSES = {
    200: ProductDetailSerializer(),
    404: response_404
}

FAVORITE_POST_RESPONSES = {
    201: {
        'properties': properties_detail,
        'example': {'detail': 'User added product'}
    },
    400: {
        'properties': properties_detail,
        'example': {'detail': 'An error has occurred'}
    },
    404: response_404,
}

FAVORITE_DELETE_RESPONSES = {
    200: {
        'properties': properties_detail,
        'example': {'detail': 'User deleted product'}
    },
}

PRODUCT_CREATE_IMAGES_RESPONSES = {
    201: None,
    404: response_404
}

PRODUCT_FILTER_RESPONSES = {
    200: inline_serializer(
        name='ProductFilter',
        fields={
            'price_min': serializers.DecimalField(max_digits=7, decimal_places=2, ),
            'price_max': serializers.DecimalField(max_digits=7, decimal_places=2, ),
            'options': ProductOptionSerializer(many=True)
        },
    )
}
