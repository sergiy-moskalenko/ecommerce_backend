from rest_framework.test import APIClient

from tests.test_accounts.conftest import *
from tests.test_store.conftest import *

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture(scope='session')
def api_client():
    yield APIClient()
