import factory
from faker import Faker

from order.models import Order, OrderItem, PaymentStatus, PaymentMode, OrderStatus, PaymentData
from tests.test_accounts.factories import gen_phone_number
from tests.test_store.factories import ProductFactory

fake = Faker(locale='uk_UA')


def lazy_attribute_factory(value_function):
    return factory.LazyAttribute(value_function)


class OrderFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = lazy_attribute_factory(lambda _: gen_phone_number())
    customer = factory.SubFactory('tests.test_accounts.factories.UserFactory')
    order_status = OrderStatus.PENDING
    payment_mode = PaymentMode.CARD
    payment_status = PaymentStatus.__empty__
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    paid = False
    total_cost = 0.0

    class Meta:
        model = Order


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('random_number', digits=1)
    cost = factory.LazyAttribute(lambda obj: (obj.discount_price or obj.price) * obj.quantity)

    @classmethod
    def create(cls, **kwargs):
        product = kwargs.pop('product', ProductFactory())
        price = product.price
        discount_price = product.discount_price
        return super().create(price=price, discount_price=discount_price, **kwargs)


class PaymentDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PaymentData

    order = factory.SubFactory(OrderFactory)
    data = factory.Faker('pydict', value_types=(str, int, float))
