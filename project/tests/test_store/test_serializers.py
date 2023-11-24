from decimal import Decimal

import pytest
from rest_framework import exceptions

from store import models
from store import serializers
from store.views import get_filtered_options

MAX_IMAGES = 5
pytestmark = pytest.mark.django_db


def test_categories_serializer(category_tree):
    data = serializers.CategoriesSerializer(category_tree, many=True).data
    assert data[0]['name'] == category_tree[0].name
    assert data[0]['slug'] == category_tree[0].slug
    assert 'children' in data[0]
    assert data[0]['children'][0]['name'] == category_tree[0].get_children()[0].name
    assert data[0]['children'][0]['slug'] == category_tree[0].get_children()[0].slug


def test_product_create_serializer(product, image_file):
    # Serializing object
    data = serializers.ProductCreateSerializer(product).data
    assert data['name'] == product.name
    assert data['description'] == product.description
    assert data['price'] == str(product.price)
    assert str(data['discount_price']) == str(product.discount_price)
    assert data['image'] == product.image
    assert data['category'] == product.category.id

    # Deserializing object
    data = dict(
        name='Test product',
        description='Test product description',
        price=199.99,
        discount_price=189.99,
        image=image_file,
        category=product.category.id
    )
    serializer = serializers.ProductCreateSerializer(data=data)
    assert serializer.is_valid(raise_exception=True)


def test_product_list_serializer(products, request_anonymous_user):
    data = serializers.ProductListSerializer(
        products,
        context={'request': request_anonymous_user},
        many=True
    ).data
    assert data[0]['id'] == products[0].id
    assert data[0]['image'] == products[0].image
    assert data[0]['name'] == products[0].name
    assert data[0]['slug'] == products[0].slug
    assert data[0]['price'] == str(products[0].price)
    assert str(data[0]['discount_price']) == str(products[0].discount_price)
    assert data[0]['favorite'] is False


def test_product_detail_serializer(request_anonymous_user, product_option_value):
    product = models.ProductOptionValue.objects.first().product
    data = serializers.ProductDetailSerializer(product, context={'request': request_anonymous_user}).data
    assert data['name'] == product.name
    assert data['price'] == str(product.price)
    assert data['description'] == product.description
    assert 'options' in data
    assert 'values' in data['options'][0]
    assert 'favorite' in data
    assert 'images' in data


@pytest.mark.parametrize(
    "image_count, expected_count",
    [
        (MAX_IMAGES, MAX_IMAGES),  # Valid case with 5 images
        (MAX_IMAGES + 1, 0),  # Invalid case with 6 images
        (0, 0)  # Empty images list
    ]
)
def test_add_product_images_serializer(product, image_file, image_count, expected_count, use_test_dir):
    images = [image_file for _ in range(image_count)]
    data = {'product': product, 'images': images}
    serializer = serializers.AddProductImagesSerializer(data=data)
    if image_count > MAX_IMAGES:
        with pytest.raises(exceptions.ValidationError):
            serializer.is_valid(raise_exception=True)
        assert 'Ensure this field has no more than 5 elements.' in serializer.errors['images']
    else:
        assert serializer.is_valid()
        serializer.save(product=product)
        assert product.images.count() == expected_count


def test_product_filter_serializer(category, product_filter):
    qs_category = models.Category.objects.filter(slug=category.slug)
    qs_categories = qs_category.get_descendants(include_self=True)
    qs_options = get_filtered_options(qs_category, qs_categories)
    data = serializers.ProductFilterSerializer(qs_options, many=True).data
    for item, option in zip(data, qs_options):
        assert item['name'] == option.name
        assert 'values' in item
        assert all(v['name'] == pv.name for v, pv in zip(item['values'], option.product_values))
