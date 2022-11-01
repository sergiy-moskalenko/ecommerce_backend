from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False, )
    image = models.ImageField(null=True, blank=True, upload_to='users/')
    phone_number = PhoneNumberField(unique=True)
    date_of_birth = models.DateField(verbose_name="Birthday", null=True, blank=True)
    email_verify_token = models.CharField(max_length=250, null=True, blank=True, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
