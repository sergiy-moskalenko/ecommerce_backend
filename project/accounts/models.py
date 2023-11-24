import binascii
import os

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token

from accounts.tasks import send_confirm_email_task, send_password_recovery_task


class UserManager(BaseUserManager):
    def create_user(self, email, password, phone_number, username, date_of_birth=None, **extra_fields):
        if not email:
            raise ValueError('User must have Email')

        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, phone_number, username, date_of_birth=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, phone_number, username, date_of_birth, **extra_fields)


def generate_security_token():
    return binascii.hexlify(os.urandom(40)).decode()


def generate_uid(user_id):
    return urlsafe_base64_encode(force_bytes(user_id))


def generate_default_token(user):
    return default_token_generator.make_token(user)


class User(AbstractUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False, )
    image = models.ImageField(null=True, blank=True, upload_to='users/')
    phone_number = PhoneNumberField(unique=True)
    date_of_birth = models.DateField(verbose_name="Birthday", null=True, blank=True)
    email_verify_token = models.CharField(default=generate_security_token, max_length=250)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def regenerate_auth_token(self):
        Token.objects.filter(user=self).delete()
        return Token.objects.create(user=self).key

    def send_confirm_email(self):
        send_confirm_email_task.delay(self.username, self.email, self.email_verify_token)

    def send_password_recovery(self):
        token = generate_default_token(self)
        send_password_recovery_task.delay(self.pk, self.username, self.email, token)
