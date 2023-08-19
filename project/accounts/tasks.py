from celery import shared_task
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.models import User


@shared_task
def send_verify_email_task(username, to_email):
    user = User.objects.get(email=to_email)
    confirmation_token = user.email_verify_token
    subject = 'Verify your email'
    message = f'Hi, {username}. Use code below to verify your email. \n  {confirmation_token}'
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=False,
    )


@shared_task
def send_reset_password_task(username, to_email):
    user = User.objects.get(email=to_email)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    subject = 'Reset your password'
    message = f'Hi, {username}. Use code below to reset the password for your account.\n {uid}/{token}'
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=False,
    )
