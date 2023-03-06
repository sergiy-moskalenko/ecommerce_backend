import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
app = Celery("ecommerce")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# test example send task every second
# app.conf.beat_schedule = {
#     'send-every-1-second': {
#         'task': 'accounts.tasks.send_ok',
#         'schedule': 1.0,
#     },
# }
