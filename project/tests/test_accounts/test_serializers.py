import pytest
from django.http import Http404
from rest_framework.exceptions import ErrorDetail, ValidationError

from accounts import serializers
from .conftest import user_default_data

pytestmark = pytest.mark.django_db


def test_register_serializer(user_factory):
    # Implement your test for RegisterSerializer
    user_data = user_default_data('date_of_birth')
    serializer = serializers.RegisterSerializer(data=user_data)

    assert serializer.is_valid(raise_exception=True)
    assert serializer.validated_data == user_data

    user_factory.create(email=user_data['email'].capitalize())
    serializer = serializers.RegisterSerializer(data=user_data)

    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)

    assert "user with this email already exists." in serializer.errors['email']


@pytest.mark.parametrize("user, password, expected_data, expected_error", [
    ('user_active', 'B#1UQnNG!3', {}, None),
    ('user_active', 'B#1UQnNG!', None, {'message': 'Incorrect Login credentials'}),
    ('user_not_active', 'B#1UQnNG!3', None, {'message': 'Please check your inbox and confirm your email address'})
])
def test_login_serializer(user, password, expected_data, expected_error, request):
    # Implement your test for LoginSerializer
    email = request.getfixturevalue(user).email
    data = {'email': email, 'password': password}
    serializer = serializers.LoginSerializer(data=data)

    if expected_error:
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        expected_key, expected_msg = expected_error.popitem()
        assert exc.value.detail == {expected_key: [ErrorDetail(expected_msg, 'invalid')]}

    if expected_data:
        assert serializer.is_valid()
        assert serializer.validated_data == expected_data


def test_login_serializer_invalid_email():
    # Implement your test for LoginSerializer
    invalid_data = {'email': 'invalid@example.com', 'password': 'some_password'}
    serializer = serializers.LoginSerializer(data=invalid_data)

    with pytest.raises(Http404):
        serializer.is_valid(raise_exception=True)


# Implement your test for PasswordRecoverySerializer
def test_password_recovery_serializer_valid(user_active):
    serializer = serializers.PasswordRecoverySerializer(data={'email': user_active.email})
    assert serializer.is_valid(raise_exception=True)
    assert serializer.validated_data['user'] == user_active


def test_password_recovery_serializer_user_not_found():
    non_existing_email = 'non_existing_email@example.com'
    serializer = serializers.PasswordRecoverySerializer(data={'email': non_existing_email})
    with pytest.raises(Http404):
        serializer.is_valid(raise_exception=True)


@pytest.mark.parametrize(
    "data, expected_err_msg",
    [
        ({'email': ''}, 'This field may not be blank.'),
        ({'email': None}, 'This field may not be null.'),
        ({'email': "invalid_email"}, 'Enter a valid email address.'),
        ({}, 'This field is required.')  # missing_email
    ])
def test_password_recovery_serializer_invalid_data(data, expected_err_msg):
    serializer = serializers.PasswordRecoverySerializer(data=data)
    assert not serializer.is_valid()
    assert 'email' in serializer.errors
    assert expected_err_msg in serializer.errors['email']


@pytest.mark.parametrize("data_set_new_password, expected_exception, expected_err_msg", [
    ('data_set_new_password_with_valid_uid_token', None, None),
    ('data_set_new_password_with_invalid_uid', Http404, None),
    ('data_set_new_password_with_invalid_token', ValidationError, 'Invalid user or token'),
])
def test_set_new_password(data_set_new_password, expected_exception, expected_err_msg, request):
    # Implement your test for SetNewPasswordSerializer
    data = request.getfixturevalue(data_set_new_password)
    serializer = serializers.SetNewPasswordSerializer(data=data)

    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            serializer.is_valid(raise_exception=True)
        if expected_err_msg:
            assert expected_err_msg in str(exc_info.value)

    else:
        assert serializer.is_valid(raise_exception=True)
        assert serializer.errors == {}


@pytest.mark.parametrize(
    "old_password, new_password, expected_valid, expected_err_msg",
    [
        ('B#1UQnNG!3', '#new_password!', True, None),
        ('incorrect_old_password', '#new_password!', False, 'Incorrect credentials'),
        ('B#1UQnNG!3', 'B#1UQnNG!3', False, "Your current password can't be with new password"),
    ]
)
def test_change_password_serializer(request_user_active, old_password, new_password, expected_valid, expected_err_msg):
    # Implement your test for ChangePasswordSerializer
    change_password_data = {
        'old_password': old_password,
        'new_password': new_password
    }
    serializer = serializers.ChangePasswordSerializer(data=change_password_data,
                                                      context={'request': request_user_active})

    assert serializer.is_valid() == expected_valid

    if expected_err_msg:
        assert expected_err_msg in serializer.errors['message'][0]
