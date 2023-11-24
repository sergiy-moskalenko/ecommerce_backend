import pytest

from order.payment import Callback
from tests.test_accounts.factories import gen_phone_number
from tests.test_order.factories import fake


@pytest.mark.django_db
def test_order_creation_with_auth_client(api_client_authenticated, products, mock_payment, mock_tgbot):
    url = '/order/'
    order_data = {
        'address': 'address',
        'city': 'city',
        'items': [
            {
                'product': products[0].id,
                'quantity': 2
            },
            {
                'product': products[1].id,
                'quantity': 1
            }
        ],
        'payment_mode': 'card',
        'card': '4242424242424242',
        'card_exp_month': '03',
        'card_exp_year': '22',
        'card_cvv': '111'
    }

    response = api_client_authenticated.post(url, data=order_data, format='json')
    assert response.status_code == 201
    assert 'order_number' in response.data


@pytest.mark.django_db
def test_order_creation_with_auth_client_2(api_client_authenticated, products, mock_tgbot):
    url = '/order/'
    order_data = {
        'address': 'address',
        'city': 'city',
        'items': [
            {
                'product': products[0].id,
                'quantity': 2
            },
            {
                'product': products[1].id,
                'quantity': 1
            }
        ],
        'payment_mode': 'cash',
    }

    response = api_client_authenticated.post(url, data=order_data, format='json')
    assert response.status_code == 201
    assert 'order_number' in response.data


@pytest.mark.django_db
def test_order_creation_with_no_auth_client(api_client, products, mock_payment, mock_tgbot):
    url = '/order/'
    order_data = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone_number': gen_phone_number(),
        'address': 'address',
        'city': 'city',
        'items': [
            {
                'product': products[0].id,
                'quantity': 2
            },
            {
                'product': products[1].id,
                'quantity': 1
            }
        ],
        'payment_mode': 'card',
        'card': '4242424242424242',
        'card_exp_month': '03',
        'card_exp_year': '22',
        'card_cvv': '111'
    }
    response = api_client.post(url, data=order_data, format='json')
    assert response.status_code == 201
    assert 'order_number' in response.data


@pytest.mark.django_db
def test_order_detail(api_client_authenticated, user_active, order_factory, order_item_factory, product):
    order = order_factory(customer=user_active)
    order_item_factory(order=order, product=product)

    response = api_client_authenticated.get(f'/order/{order.id}')
    assert response.status_code == 200


@pytest.mark.django_db
def test_pay_callback_view_signature_match(mocker, api_client, order_factory):
    order = order_factory.create(id=123)
    mocker.patch.object(Callback, 'callback', return_value={'order_id': order.id, 'status': 'success'})

    request_data = {
        'data': 'sample_data',
        'signature': 'valid_signature'
    }

    response = api_client.post('/order/paycallback', data=request_data, format='json')
    order.refresh_from_db()
    assert response.status_code == 204
    assert order.payment_status == 'success'


@pytest.mark.django_db
def test_pay_callback_view_signature_mismatch(mocker, api_client):
    request_data = {
        'data': 'sample_data',
        'signature': 'invalid_signature'
    }
    response = api_client.post('/order/paycallback', data=request_data, format='json')

    assert response.status_code == 400
    assert "Signature doesn't much, original signature" == response.data['signature']


@pytest.mark.django_db
def test_pay_callback_view_order_not_found(mocker, api_client):
    mocker.patch.object(Callback, 'callback', return_value={'order_id': 999, 'status': 'success'})

    request_data = {
        'data': 'sample_data',
        'signature': 'valid_signature'
    }
    response = api_client.post('/order/paycallback', data=request_data, format='json')

    assert response.status_code == 404
    assert 'Order not found' in response.data
