import random

import factory
from faker import Faker

from accounts.models import User

fake = Faker(locale='uk_UA')


def gen_phone_number():
    return f'+380{random.choice([50, 66, 97])}{random.randrange(10 ** 6, 10 ** 7)}'


def lazy_attribute_factory(value_function):
    return factory.LazyAttribute(value_function)


class UserFactory(factory.django.DjangoModelFactory):
    first_name = lazy_attribute_factory(lambda _: fake.first_name())
    last_name = lazy_attribute_factory(lambda _: fake.last_name())
    email = factory.Faker("safe_email")
    username = lazy_attribute_factory(lambda _: fake.user_name())
    phone_number = lazy_attribute_factory(lambda _: gen_phone_number())
    password = factory.PostGenerationMethodCall('set_password', 'B#1UQnNG!3')
    date_of_birth = factory.Faker("date_of_birth", minimum_age=10, maximum_age=100)
    is_active = False

    class Meta:
        model = User
