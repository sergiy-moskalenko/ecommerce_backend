import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

pytestmark = pytest.mark.django_db


def test_product_discount_percent_property(product_factory):
    # Create a Product instance with a discount price
    product = product_factory.build(price=100, discount_price=20)
    assert product.discount_percent == 80  # (100 - 20) / 100 = 0.8 * 100 = 80

    # Create a Product instance without a discount price
    product = product_factory.build(price=100, discount_price=None)
    assert product.discount_percent is None


def test_product_clean_method(product_factory):
    # Discount price less than price should raise a ValidationError
    product = product_factory.build(price=100, discount_price=120)
    with pytest.raises(ValidationError, match=f"Discount price: 120 must be less than price: 100"):
        product.clean()

    # Discount price of 0 should raise a ValidationError
    product = product_factory.build(price=100, discount_price=0)
    with pytest.raises(ValidationError, match="Discount price can't be 0. Maybe you wanted to leave it empty"):
        product.clean()


def test_product_slug_generation(product_factory):
    # Test slug generation in the save method
    product = product_factory.create(name="Test Product")
    assert product.slug == "test-product"

    # Test that an existing slug is not modified on save
    product = product_factory.create(name="Test Product #2", slug="test-product-2")
    assert product.slug == "test-product-2"


def test_product_str_method(product_factory):
    # Test the __str__ method
    product = product_factory.build(name="Test Product", price=100)
    assert str(product) == "Test Product"


def test_price_not_negative(product_factory, category):
    # Test the price constraint
    instance = product_factory.build(price=10, category=category)
    instance.save()

    instance = product_factory.build(price=-5, category=category)
    with pytest.raises(IntegrityError):
        instance.save()


def test_discount_price_not_zero(product_factory, category):
    # Test the discount_price constraint
    instance = product_factory.build(discount_price=None, category=category)
    instance.save()

    instance = product_factory.build(discount_price=0, category=category)
    with pytest.raises(IntegrityError):
        instance.save()


def test_price_more_than_discount_price(product_factory, category):
    # Test the price more than discount_price constraint
    instance = product_factory.build(price=20, discount_price=15, category=category)
    instance.save()

    instance = product_factory.build(price=10, discount_price=15, category=category)
    with pytest.raises(IntegrityError):
        instance.save()
