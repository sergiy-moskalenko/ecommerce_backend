from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, email, password, phone_number, username):
        if not email:
            raise ValueError('User must have Email')

        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, phone_number, username):
        user = self.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False, )
    image = models.ImageField(null=True, blank=True, upload_to='users/')
    phone_number = PhoneNumberField(unique=True)
    date_of_birth = models.DateField(verbose_name="Birthday", null=True, blank=True)
    email_verify_token = models.CharField(max_length=250, null=True, blank=True, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']
