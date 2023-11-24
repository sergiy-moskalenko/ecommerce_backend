import pytest
from rest_framework.test import APIClient

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture(scope='session')
def api_client():
    yield APIClient()
