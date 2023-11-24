from decimal import Decimal
from math import floor, ceil

import pytest
from django.db.models import Case, When
from django.db.models import DecimalField

from store import serializers
from store.filters import filter_by_values, filter_by_price, filter_by_name, order_by_price
from store.models import Value, Product
from tests.test_store.conftest import COUNT_PRODUCTS

pytestmark = pytest.mark.django_db


def test_get_categories(api_client, category_tree):
    """ Test CategoriesListView list method """

    url = '/store/categories'
    response = api_client.get(url)
    expected_data = serializers.CategoriesSerializer(category_tree, many=True).data
    assert response.status_code == 200
    assert len(response.data) == len(category_tree)
    assert response.data == expected_data


def test_get_products_by_category(api_client, category, products, request_user_active):
    """ Test ProductListView list method """

    url = f'/store/categories/{category.slug}/products'
    response = api_client.get(url)
    expected_json = serializers.ProductListSerializer(products, context={'request': request_user_active},
                                                      many=True).data
    assert response.status_code == 200
    assert len(response.data) == COUNT_PRODUCTS
    assert response.data == expected_json


def test_get_product_detail(api_client, product, request_anonymous_user):
    """ Test ProductDetailView get method """

    url = f'/store/product/{product.slug}'
    response = api_client.get(url)
    expected_json = serializers.ProductDetailSerializer(product, context={'request': request_anonymous_user}).data
    assert response.status_code == 200
    assert response.data['favorite'] is False
    assert response.data == expected_json


def test_favorite_product_detail(api_client_authenticated, favorite_product, request_user_active):
    """ Test ProductDetailView get method """

    url = f'/store/product/{favorite_product.slug}'
    response = api_client_authenticated.get(url)
    expected_json = serializers.ProductDetailSerializer(favorite_product, context={'request': request_user_active}).data
    assert response.status_code == 200
    assert response.data['favorite'] is True
    assert response.data == expected_json


@pytest.mark.parametrize(
    'client, expected_status',
    [
        ('api_client_authenticated', 403),
        ('api_client_auth_admin', 201),
        ('api_client_auth_with_perm', 201),
        ('api_client_auth_with_group_perm', 201)
    ]
)
def test_create_product(category, client, expected_status, request):
    """ Test ProductCreateView post method """

    url = '/store/product/create'
    data = {
        "name": "Test Product",
        "description": "Test description",
        "price": "100.00",
        "discount_price": "89.99",
        "category": category.id
    }
    api_client = request.getfixturevalue(client)
    response = api_client.post(url, data, format='json')
    assert response.status_code == expected_status


def test_add_product_image(api_client_auth_admin, product, image_file, use_test_dir):
    """ Test AddProductImagesView post method """

    url = f'/store/product/{product.slug}/add/images'
    data = {
        'images': [image_file]
    }
    response = api_client_auth_admin.post(url, data, format="multipart")
    assert response.status_code == 201
    assert response.data == {}


def test_favorite_product(product, api_client_authenticated, favorite_product):
    """ Test FavoriteProductAddDeleteView post/delete method """

    # Test to add product to favorites
    url = f'/store/product/{product.slug}/favorite'
    response = api_client_authenticated.post(url)
    assert response.status_code == 200
    assert response.data == {'detail': 'User added product'}

    # Test bad_request to add product to favorites
    url = f'/store/product/bad_request/favorite'
    response = api_client_authenticated.post(url)
    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}

    # Test when favorite exists
    url = f'/store/product/{favorite_product.slug}/favorite'
    response = api_client_authenticated.post(url)
    assert response.status_code == 400
    assert response.data == {'detail': 'An error has occurred'}

    # Test to delete product to favorites
    url = f'/store/product/{product.slug}/favorite'
    response = api_client_authenticated.delete(url)
    assert response.status_code == 200
    assert response.data == {'detail': 'User deleted product'}


def test_get_filters_products_by_category(category, product_filter, api_client_authenticated):
    """ Test ProductFilterListView list method """

    url = f'/store/categories/{category.slug}/filter'
    response = api_client_authenticated.get(url)
    assert response.status_code == 200
    assert 'price_min' in response.data
    assert 'price_max' in response.data
    assert 'options' in response.data


@pytest.mark.parametrize('order_price', ['-price', 'price', ])
def test_get_products_by_category_with_filter_product(api_client, category, product_filter, order_price):
    """ Test ProductListView list method with query parameters """

    values_to_filter = ['15.6 inch', 'black', 'silver']
    values_ids = Value.objects.filter(name__in=values_to_filter).values_list('id', flat=True)
    values_str = ",".join(map(str, values_ids))  # '2,10,11'

    price_min_query, price_max_query = get_min_max_actual_prices(category)
    search_query = 'laptop'

    query_params = {
        'value': values_str,
        'o': order_price,
        's': search_query,
        'price_min': price_min_query,
        'price_max': price_max_query
    }

    url = f'/store/categories/{category.slug}/products?{query_params}'
    response = api_client.get(url, query_params)
    data = response.data

    queryset = get_filtered_products(category, order_price, search_query, values_str, price_min_query,
                                     price_max_query)

    assert response.status_code == 200
    assert len(data) == queryset.count()

    # Checking that the prices are sorted in the expected order
    assert_prices_sorted(data, order_price)

    # Checking that all returned products have the word 'laptop' in their names
    assert_products_contain_search_query(data, search_query)

    # Checking that response prices do not exceed the maximum and minimum prices
    assert_response_prices_within_range(data, price_max_query, price_min_query)


def get_actual_prices(category):
    return (
        Product.objects.filter(category=category)
        .annotate(
            actual_price=Case(
                When(discount_price__isnull=False, then='discount_price'),
                default='price',
                output_field=DecimalField()
            )
        )
        .order_by('actual_price')
        .values_list('actual_price', flat=True)
    )


def get_filtered_products(category, order_price, search_query, values_str, price_min_query, price_max_query):
    qs_products = Product.objects.filter(category__slug=category.slug)
    queryset = filter_by_values(qs_products, values_str)
    queryset = filter_by_name(queryset, search_query)
    queryset = filter_by_price(queryset, price_min_query, price_max_query)
    queryset = order_by_price(queryset, [order_price])
    return queryset


def get_min_max_actual_prices(category):
    actual_prices = get_actual_prices(category)
    price_min_query, price_max_query = floor(actual_prices[4]), ceil(actual_prices[COUNT_PRODUCTS - 4])
    return price_min_query, price_max_query


def assert_products_contain_search_query(data, search_query):
    assert all(search_query in product['name'].lower() for product in data)


def assert_response_prices_within_range(data, price_max_query, price_min_query):
    for product in data:
        product_price = Decimal(product['discount_price'] or product['price'])
        assert price_min_query <= product_price <= price_max_query


def assert_prices_sorted(data, order_price):
    if order_price == '-price':
        assert all(
            Decimal(data[i]['discount_price'] or data[i]['price']) >=
            Decimal(data[i + 1]['discount_price'] or data[i + 1]['price'])
            for i in range(len(data) - 1)
        )
    else:
        assert all(
            Decimal(data[i]['discount_price'] or data[i]['price']) <=
            Decimal(data[i + 1]['discount_price'] or data[i + 1]['price'])
            for i in range(len(data) - 1)
        )
