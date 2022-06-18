import pytest

from ksatria_muslim.users.models import User
from ksatria_muslim.users.tests.factories import UserFactory
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def api_client():
    return APIClient()
