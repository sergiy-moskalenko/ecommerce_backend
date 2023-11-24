import pytest
from rest_framework.exceptions import ValidationError

from order import models
from order.serializers import OrderListCreateSerializer
from tests.test_accounts.factories import gen_phone_number


def order_data_with_payment_card():
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': gen_phone_number(),
        'city': 'Sample City',
        'address': 'Sample Address',
        'payment_mode': models.PaymentMode.CARD,
        'card': '4242424242424242',
        'card_exp_month': '03',
        'card_exp_year': '22',
        'card_cvv': '111'
    }


@pytest.fixture
def order_items_data(products):
    return {
        'items': [
            {
                'product': products[0].id,
                'quantity': 2
            },
            {
                'product': products[1].id,
                'quantity': 1
            }
        ]
    }


# Pytest function to test validation of OrderListCreateSerializer
def test_order_list_create_serializer_with_auth_user(db, request_user_active, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    del order_data['first_name']
    del order_data['last_name']
    del order_data['phone_number']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_user_active}
    )
    assert serialized_data.is_valid()


def test_order_list_create_serializer_with_anon_user(db, request_anonymous_user, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_anonymous_user}
    )
    assert serialized_data.is_valid()


def test_order_list_create_serializer_payment_cash(db, request_anonymous_user, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    order_data['payment_mode'] = models.PaymentMode.CASH
    del order_data['card']
    del order_data['card_exp_month']
    del order_data['card_exp_year']
    del order_data['card_cvv']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_anonymous_user}
    )
    assert serialized_data.is_valid()


def test_order_serializer_invalid_payment_mode(db, request_anonymous_user, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    order_data['payment_mode'] = 'invalid'
    serializer = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_anonymous_user}
    )
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


def test_missing_required_card_fields(db, request_anonymous_user, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    del order_data['card']
    del order_data['card_exp_month']
    del order_data['card_exp_year']
    del order_data['card_cvv']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_anonymous_user}
    )
    with pytest.raises(ValidationError):
        serialized_data.is_valid(raise_exception=True)


def test_missing_required_first_name_and_last_name(db, request_user_no_name, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    del order_data['first_name']
    del order_data['last_name']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_user_no_name}
    )
    with pytest.raises(ValidationError):
        serialized_data.is_valid(raise_exception=True)


def test_missing_required_images(db, request_user_no_name):
    order_data = order_data_with_payment_card()
    del order_data['first_name']
    del order_data['last_name']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_user_no_name}
    )
    with pytest.raises(ValidationError):
        serialized_data.is_valid(raise_exception=True)


def test_missing_required_incorrect_card_cvv(db, request_anonymous_user, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    del order_data['card']
    del order_data['card_exp_month']
    del order_data['card_exp_year']
    del order_data['card_cvv']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_anonymous_user}
    )
    with pytest.raises(ValidationError):
        serialized_data.is_valid(raise_exception=True)


def test_missing_required_no_user_and_not_first_name_and_last_name(db, request_anonymous_user, order_items_data):
    order_data = order_data_with_payment_card()
    order_data.update(order_items_data)
    del order_data['first_name']
    del order_data['last_name']
    serialized_data = OrderListCreateSerializer(
        data=order_data,
        context={'request': request_anonymous_user}
    )
    with pytest.raises(ValidationError) as exc:
        serialized_data.is_valid(raise_exception=True)
