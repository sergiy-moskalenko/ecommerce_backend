import pytest
from rest_framework.exceptions import ErrorDetail

from accounts.models import User
from .conftest import user_default_data
from .factories import fake

pytestmark = pytest.mark.django_db


def get_response(client, url, params=None):
    response = client.post(url, params, format='json')
    return response.status_code, response.data


# TEST_CREATE_USER
user_data_cases = [
    (user_default_data(), 201, user_default_data('password')),
    (user_default_data(username=''), 400, {'username': ['This field may not be blank.']}),
    (user_default_data(email=''), 400, {'email': ['This field may not be blank.']}),
    (user_default_data(phone_number=''), 400, {'phone_number': ['This field may not be blank.']}),
    (user_default_data('date_of_birth'), 201, user_default_data('password', date_of_birth=None)),
    (user_default_data(password=''), 400, {'password': ['This field may not be blank.']}),
]


@pytest.mark.parametrize("params, expected_status, expected_data", user_data_cases)
def test_create_user(api_client, params, expected_status, expected_data):
    url = '/accounts/register'
    status_code, response_data = get_response(api_client, url, params)
    assert status_code == expected_status
    assert response_data == expected_data


# TEST_CONFIRM_EMAIL
@pytest.mark.parametrize(
    'token, expected_status, expected_message',
    [
        ('confirm_email_with_not_active_token', 204, None),  # Test valid token
        ('confirm_email_with_invalid_token', 400, {'message': 'Invalid activation token'}),  # Test invalid token
        ('confirm_email_with_active_token', 204, None)  # Test active valid token
    ]
)
def test_confirm_email(api_client, token, expected_status, expected_message, request):
    url = '/accounts/confirm-email'
    verify_token = request.getfixturevalue(token)
    params = {'email_verify_token': verify_token}
    status_code, response_data = get_response(api_client, url, params)
    assert status_code == expected_status
    assert response_data == expected_message


# TEST_LOGIN_USER
@pytest.mark.parametrize(
    'credentials, expected_status, expected_data',
    [
        # Test valid credentials
        ({'email': 'valid_email@example.com', 'password': 'B#1UQnNG!3'},
         201,
         'token'),
        # Test invalid password
        ({'email': 'valid_email@example.com', 'password': 'B#1UQnNG!'},
         400,
         {'message': ['Incorrect Login credentials']}),
        # Test invalid email
        ({'email': 'invalid_email@example', 'password': 'B#1UQnNG!3'},
         400,
         {'email': ['Enter a valid email address.']}),
        # Test missing password
        ({'email': 'valid_email@example.com'},
         400,
         {'password': ['This field is required.']}),
        # Test missing email
        ({'password': 'B#1UQnNG!3'},
         400,
         {'email': ['This field is required.']}),
        # Test not active user
        ({'email': 'not_active_email@example.com', 'password': 'B#1UQnNG!3'},
         400,
         {'message': ['Please check your inbox and confirm your email address']}),
        # Test defunct user
        ({'email': 'defunct_mail@example.com', 'password': 'B#1UQnNG!3'},
         404,
         {'detail': ErrorDetail(string='Not found.', code='not_found')})
    ]
)
def test_login_user(api_client, user_active, user_not_active, credentials, expected_status, expected_data):
    url = '/accounts/login'
    status_code, response_data = get_response(api_client, url, credentials)
    assert status_code == expected_status
    if isinstance(expected_data, str):
        assert expected_data in response_data
    else:
        assert response_data == expected_data


# TEST_LOGOUT_USER
@pytest.mark.parametrize(
    'client_, expected_status, expected_data',
    [
        ('api_client_authenticated', 204, None),
        ('api_client', 401, {'detail': 'Authentication credentials were not provided.'}),
        ('api_client_invalid_authenticated', 401, {'detail': 'Invalid token.'})
    ]
)
def test_logout_user(client_, expected_status, expected_data, request):
    url = '/accounts/logout'
    client = request.getfixturevalue(client_)
    response = client.delete(url, format='json')
    status_code, response_data = response.status_code, response.data
    assert status_code == expected_status
    assert response_data == expected_data


#  TEST_PASSWORD_RECOVERY_EMAIL
@pytest.mark.parametrize(
    'email_test, expected_status, expected_data',
    [
        ('valid_email@example.com', 204, None),
        ('defunct_mail@example.com', 404, {'detail': "Not found."})
    ]
)
def test_password_recovery_email(api_client, user_active, email_test, expected_status, expected_data):
    url = '/accounts/password-recovery'
    params = {'email': email_test}
    status_code, response_data = get_response(api_client, url, params)
    assert status_code == expected_status
    assert response_data == expected_data


#  TEST_SET_PASSWORD
@pytest.mark.parametrize(
    'params_set_new_password, expected_status, expected_data',
    [
        ('data_set_new_password_with_valid_uid_token', 204, None),
        ('data_set_new_password_with_invalid_token', 400, {'message': ['Invalid user or token']}),
        ('data_set_new_password_with_invalid_uid', 404, {'detail': "Not found."}),
    ]
)
def test_set_new_password(api_client, params_set_new_password, expected_status, expected_data, user_active, request):
    url = '/accounts/set-password'
    params = request.getfixturevalue(params_set_new_password)
    response = api_client.post(url, params, format='json')
    status_code, response_data = response.status_code, response.data
    assert status_code == expected_status
    assert response_data == expected_data


#  TEST_PASSWORD_CHANGE
@pytest.mark.parametrize(
    'params, expected_status, expected_data',
    [
        ({'old_password': 'B#1UQnNG!3', 'new_password': fake.password()},
         200,
         {}),
        ({'old_password': 'B#1UQnNG!3', 'new_password': 'B#1UQnNG!3'},
         400,
         {'message': ["Your current password can't be with new password"]}),
        ({'old_password': 'B#1UQnNG!', 'new_password': fake.password()},
         400,
         {'message': ['Incorrect credentials']}),
    ]
)
def test_password_change(user_active, api_client_authenticated, params, expected_status, expected_data):
    url = f'/accounts/change-password'
    response = api_client_authenticated.put(url, params, format='json')
    status_code, response_data = response.status_code, response.data
    assert status_code == expected_status
    assert response_data == expected_data
    if status_code == 200:
        user_active.refresh_from_db()
        assert user_active.check_password(params['new_password'])
