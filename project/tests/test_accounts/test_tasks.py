import pytest

from accounts.models import generate_default_token
from accounts.tasks import (
    send_confirm_email_task,
    send_password_recovery_task
)


@pytest.mark.celery(task_always_eager=True)
@pytest.mark.django_db(transaction=True)
def test_send_celery_confirm_email_task(celery_app, celery_worker, user_active):
    result = send_confirm_email_task.delay(
        user_active.username,
        user_active.email,
        user_active.email_verify_token
    )
    assert result.get()


@pytest.mark.django_db(transaction=True)
def test_send_password_recovery_task(celery_app, celery_worker, user_active):
    token = generate_default_token(user_active)
    result = send_password_recovery_task.delay(
        user_active.pk,
        user_active.username,
        user_active.email,
        token
    )
    assert result.get()
