from smtplib import SMTPException

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError
from django.core.mail import send_mail


def send_email(subject, message, emails, from_email=settings.EMAIL_HOST_USER, html_message=None):
    try:
        return send_mail(subject, message, from_email, [emails], html_message=html_message, fail_silently=False)
    except (BadHeaderError, SMTPException):
        raise ValidationError(f'Failed to send email. Please retry later.')
