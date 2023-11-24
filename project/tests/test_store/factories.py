import random
from decimal import Decimal

import factory.fuzzy
from faker import Faker

from store import models
from tests.test_accounts.factories import UserFactory

fake = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Category_{n}')

    class Meta:
        model = models.Category


class ProductFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    name = factory.LazyAttribute(lambda x: fake.name())
    price = factory.fuzzy.FuzzyDecimal(0.99, 999.99)
    # discount_price = factory.LazyAttribute(lambda _self: _self.price - round(_self.price * Decimal(0.1), 2))
    description = factory.LazyAttribute(lambda x: fake.text())

    @factory.lazy_attribute
    def discount_price(self):
        if random.choice([True, False]):
            return self.price - round(self.price * Decimal(0.1), 2)

    class Meta:
        model = models.Product


class OptionFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda x: fake.name())

    class Meta:
        model = models.Option


class ValueFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda x: fake.name())
    option = factory.SubFactory(OptionFactory)

    class Meta:
        model = models.Value


class ProductOptionValueFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    option = factory.SubFactory(OptionFactory)
    value = factory.SubFactory(ValueFactory)

    class Meta:
        model = models.ProductOptionValue


class FavoriteFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Favorite


class ProductImageFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField()

    class Meta:
        model = models.ProductImage


class ProductFilterFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    option = factory.SubFactory(OptionFactory)
    position = None

    class Meta:
        model = models.ProductFilter
