import pytest
from pytest_factoryboy import register
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

from accounts.models import generate_default_token, generate_uid
from .factories import UserFactory

register(UserFactory)
register(UserFactory, "user_active", email='valid_email@example.com', is_active=True)
register(UserFactory, "user_not_active", email='not_active_email@example.com')


def user_default_data(*args, **kwargs) -> dict:  # v2 (remove_field: str | None = None)
    user = {
        'username': 'test50',
        'email': 'yskoryk@example.com',
        'phone_number': '+380667603208',
        'date_of_birth': '2018-08-08',
        'password': '*e4chYgLy('
    }
    for arg in args:
        if arg and arg in user:
            del user[arg]
    # v2
    # if remove_field and remove_field in user:
    #     del user[remove_field]
    user.update(kwargs)
    return user


@pytest.fixture
def confirm_email_with_not_active_token(user):
    yield user.email_verify_token


@pytest.fixture
def confirm_email_with_invalid_token(user_active):
    yield user_active.email_verify_token[::-1]


@pytest.fixture
def confirm_email_with_active_token(user_active):
    yield user_active.email_verify_token


@pytest.fixture
def token_auth(db, user_active):
    token, _ = Token.objects.get_or_create(user=user_active)
    return token.key


@pytest.fixture
def api_client_authenticated(api_client, token_auth):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token_auth)
    yield api_client
    api_client.credentials()


@pytest.fixture
def api_client_invalid_authenticated(api_client, token_auth):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token_auth[::-1])
    yield api_client
    api_client.credentials()


@pytest.fixture
def data_set_new_password_with_valid_uid_token(user_active):
    uid = generate_uid(user_active.pk)
    token = generate_default_token(user_active)
    return dict(uid=uid, token=token, password='#new_password!')


@pytest.fixture
def data_set_new_password_with_invalid_uid(user_active):
    uid = generate_uid(user_active.id + 1)
    token = generate_default_token(user_active)
    return dict(uid=uid, token=token, password='#new_password!')


@pytest.fixture
def data_set_new_password_with_invalid_token(user_active):
    uid = generate_uid(user_active.pk)
    token = generate_default_token(user_active)[:-1]
    return dict(uid=uid, token=token, password='#new_password!')


@pytest.fixture
def request_user_active(user_active):
    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = user_active
    return request
