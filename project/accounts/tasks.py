from celery import shared_task

from accounts.utils import send_email


@shared_task
def send_confirm_email_task(username, to_email, confirmation_token):
    subject = 'Confirm your email'
    message = f'Hi, {username}. Use the code below to confirm your email. \n  {confirmation_token}'
    return send_email(subject, message, to_email)


@shared_task
def send_password_recovery_task(pk, username, to_email, token):
    from accounts.models import generate_uid
    uid = generate_uid(pk)
    subject = 'Recovery your password'
    message = f'Hi, {username}. Use the code below to recovery the password for your account.\n {uid}/{token}'
    return send_email(subject, message, to_email)
