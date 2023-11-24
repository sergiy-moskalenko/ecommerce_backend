import logging
import random
import shutil
from io import BytesIO

import pytest
from PIL import Image
from django.core.files.base import File
from pytest_factoryboy import register

from store.models import Option, Category
from .factories import (
    CategoryFactory,
    FavoriteFactory,
    ProductOptionValueFactory,
    ProductFactory,
    ProductFilterFactory,
    ProductImageFactory,
    OptionFactory,
    ValueFactory,
)
from .factories import factory

register(CategoryFactory)
register(FavoriteFactory)
register(ProductFactory)
register(ProductOptionValueFactory)
register(ProductFilterFactory)
register(ProductImageFactory)
register(OptionFactory)
register(ValueFactory)

logger = logging.getLogger(__name__)

TEST_DIR = 'test_data'
COUNT_PRODUCTS = 50


@pytest.fixture
def category(category_factory):
    return category_factory.create(name='notebook')


@pytest.fixture
def category_tree(db):
    data = {
        'name': 'category_a',
        'slug': 'category_a',
        'children': [
            {
                'name': 'category_b',
                'slug': 'category_b',
                'children': [
                    {
                        'name': 'category_c',
                        'slug': 'category_c',
                        'children': []
                    }
                ]
            }
        ],
    }
    records = Category.objects.build_tree_nodes(data)
    Category.objects.bulk_create(records)
    Category.objects.create(name='category_d')
    return Category.objects.get_cached_trees()


@pytest.fixture
def product(category, product_factory):
    return product_factory.create(category=category)


@pytest.fixture
def favorite_product(product_factory, category, user_active):
    product = product_factory.create(category=category)
    product.favorites.create(user=user_active)
    return product


@pytest.fixture
def products(category, product_factory):
    return product_factory.create_batch(
        size=COUNT_PRODUCTS,
        category=category,
        name=factory.Sequence(lambda n: f'{random.choice(["Noutbuk", "Laptop"])}_{n}')
    )


@pytest.fixture
def options_values_dict():
    return {
        "Display size": ['17 inch', '15.6 inch', '13 inch'],
        "Video card": ['nvidia gtx 1660', 'nvidia RTX 3060', 'radeon'],
        "Ram size": ['8 GB', '16 GB', '32 GB'],
        "Color": ['silver', 'black', 'white'],
        "SSD size": ['512 GB', '1 TB', '2 TB']
    }


@pytest.fixture
def options_dict(options_values_dict, option_factory):
    return {name: option_factory.create(name=name) for name in options_values_dict}


@pytest.fixture
def values_dict(options_values_dict, value_factory, options_dict):
    return {name: [value_factory.create(option=options_dict[name], name=value) for value in values]
            for name, values in options_values_dict.items()}


@pytest.fixture
def product_option_value(
        product_option_value_factory,
        products,
        options_values_dict,
        options_dict,
        values_dict,
):
    for product in products:
        for option_name, option_values in options_values_dict.items():
            product_option_value_factory.create(
                product=product,
                option=options_dict[option_name],
                value=random.choice(values_dict[option_name])
            )


@pytest.fixture
def product_filter(
        product_option_value,
        product_filter_factory,
        category,
        options_dict,
        values_dict,
):
    positions = range(1, len(options_dict.values()) + 1)
    for option, position in zip(options_dict, positions):
        instance_option = Option.objects.filter(name=option).first()
        product_filter_factory.create(category=category, option=instance_option, position=position)


@pytest.fixture
def image_file(request):
    file = BytesIO()
    image = Image.new("RGB", size=(50, 50))
    image.save(file, 'png')
    file.seek(0)
    return File(file, name='test.png')


@pytest.fixture
def use_test_dir(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / TEST_DIR
    yield
    try:
        shutil.rmtree(settings.MEDIA_ROOT.name)
        logger.info(f"Folder '{settings.MEDIA_ROOT.name}' deleted successfully.")
    except OSError as e:
        logger.info(f"Error: '{settings.MEDIA_ROOT.name}' - {e.strerror}")
