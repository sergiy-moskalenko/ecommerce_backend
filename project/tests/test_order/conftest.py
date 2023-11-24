import pytest
from pytest_factoryboy import register

from .factories import OrderFactory, OrderItemFactory, PaymentDataFactory

register(OrderFactory)
register(OrderItemFactory)
register(PaymentDataFactory)


@pytest.fixture
def order():
    return OrderFactory()


@pytest.fixture
def mock_payment(mocker):
    mocker.patch('order.views.payment.LiqPayCard')


@pytest.fixture
def mock_tgbot(mocker):
    mocker.patch('order.views.send_message_to_tg')
