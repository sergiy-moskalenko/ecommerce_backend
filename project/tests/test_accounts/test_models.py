import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.authtoken.models import Token

from accounts.models import User, generate_security_token, generate_default_token
from accounts.tasks import send_confirm_email_task, send_password_recovery_task
from tests.test_accounts.conftest import user_default_data


def test_create_user_with_required_fields(db):
    user_data = user_default_data()
    user = User.objects.create_user(**user_data)
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.phone_number == user_data["phone_number"]
    assert user.check_password(user_data["password"])
    assert user.is_active is False
    assert user.is_staff is False
    assert user.is_superuser is False


def test_create_user_missing_email(db):
    user_data = user_default_data(email="")
    with pytest.raises(ValueError, match="User must have Email"):
        User.objects.create_user(**user_data)


def test_create_superuser(db):
    user_data = user_default_data()
    superuser = User.objects.create_superuser(**user_data)
    assert User.objects.filter(email=user_data['email']).exists()
    assert superuser.check_password(user_data['password'])
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True


def test_create_user_duplicate_email(db, user_factory):
    user_factory.create(email='duplicate@example.com')
    with pytest.raises(IntegrityError):
        user_factory.create(email='duplicate@example.com')


def test_generate_security_token():
    token = generate_security_token()
    assert len(token) == 80


def test_user_model_str_method(db, user_factory):
    user = user_factory.create(email="test@example.com")
    assert str(user) == "test@example.com"


def test_regenerate_auth_token(db, user_active):
    old_token = Token.objects.create(user=user_active).key
    new_token = user_active.regenerate_auth_token()
    assert old_token != new_token
    assert Token.objects.filter(user=user_active).count() == 1


def test_send_verification_email(db, user_not_active, mocker):
    mocker.patch('accounts.tasks.send_confirm_email_task.delay')
    user_not_active.send_confirm_email()
    send_confirm_email_task.delay.assert_called_once_with(
        user_not_active.username,
        user_not_active.email,
        user_not_active.email_verify_token
    )


def test_send_password_recovery(db, user_active, mocker):
    token = generate_default_token(user_active)
    mocker.patch('accounts.tasks.send_password_recovery_task.delay')
    user_active.send_password_recovery()
    send_password_recovery_task.delay.assert_called_once_with(
        user_active.pk,
        user_active.username,
        user_active.email,
        token
    )
