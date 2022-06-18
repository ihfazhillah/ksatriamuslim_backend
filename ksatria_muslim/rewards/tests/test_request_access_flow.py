import pytest
from django.urls import reverse
from factory import Faker
from factory.django import DjangoModelFactory

from ksatria_muslim.children.models import Child
from ksatria_muslim.packages.models import Package
from ksatria_muslim.rewards.models import RewardHistory
from ksatria_muslim.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def parent():
    return UserFactory()


class ChildFactory(DjangoModelFactory):
    class Meta:
        model = Child


@pytest.fixture
def child(parent):
    return ChildFactory(parent=parent, name="hello_child")


class PackageFactory(DjangoModelFactory):
    title = Faker("sentence")

    class Meta:
        model = Package


@pytest.fixture
def package():
    return PackageFactory(price=10, length=10)


class RewardHistoryFactory(DjangoModelFactory):
    class Meta:
        model = RewardHistory


def test_flow_request_access(api_client, parent, child, package):
    RewardHistoryFactory.create(count=20, description="Haha", child=child)
    api_client.force_authenticate(parent)

    buy_package_url = reverse("api:rewardhistory-buy-package")

    # child belum punya package
    resp = api_client.post(
        buy_package_url,
        data={
            "child": child.id,
            "package": package.title
        }
    )

    resp_data = resp.json()
    assert resp_data["permissible"]
    assert resp_data["duration_remaining"] == 10
    assert resp_data["coin_remaining"] == 10

    # child belum sempat pakai, tapi sudah punya package
    resp = api_client.post(
        buy_package_url,
        data={
            "child": child.id,
            "package": package.title
        }
    )
    resp_data = resp.json()
    assert resp_data["permissible"]
    assert resp_data["duration_remaining"] == 10
    assert resp_data["coin_remaining"] == 10

    # child menggunakan package, start at
    log_package_usage_url = reverse("api:packageusage-log")
    resp = api_client.post(
        log_package_usage_url,
        data={
            "child": child.id,
            "package": package.title,
            "started_at": "202201010100",
            # "finished_at": None
        }
    )
    assert resp.json()["ok"]

    # kepakai 1 menit
    log_package_usage_url = reverse("api:packageusage-log")
    resp = api_client.post(
        log_package_usage_url,
        data={
            "child": child.id,
            "package": package.title,
            "finished_at": "202201010101",
            # "started_at": None
        }
    )
    assert resp.json()["ok"]

    resp = api_client.post(
        buy_package_url,
        data={
            "child": child.id,
            "package": package.title
        }
    )
    resp_data = resp.json()
    assert resp_data["permissible"]
    assert resp_data["duration_remaining"] == 9
    assert resp_data["coin_remaining"] == 10

    # child menggunakan menghabiskan package
    log_package_usage_url = reverse("api:packageusage-log")
    resp = api_client.post(
        log_package_usage_url,
        data={
            "child": child.id,
            "package": package.title,
            "started_at": "202201010200",
            # "finished_at": None
        }
    )
    assert resp.json()["ok"]

    log_package_usage_url = reverse("api:packageusage-log")
    resp = api_client.post(
        log_package_usage_url,
        data={
            "child": child.id,
            "package": package.title,
            "finished_at": "202201010209",
            # "started_at": None
        }
    )
    assert resp.json()["ok"]

    resp = api_client.post(
        buy_package_url,
        data={
            "child": child.id,
            "package": package.title
        }
    )
    resp_data = resp.json()
    assert resp_data["permissible"]
    assert resp_data["coin_remaining"] == 0
    assert resp_data["duration_remaining"] == 10

    # child menggunakan menghabiskan lagi
    log_package_usage_url = reverse("api:packageusage-log")
    resp = api_client.post(
        log_package_usage_url,
        data={
            "child": child.id,
            "package": package.title,
            "started_at": "202201010200",
            # "finished_at": None
        }
    )
    assert resp.json()["ok"]

    log_package_usage_url = reverse("api:packageusage-log")
    resp = api_client.post(
        log_package_usage_url,
        data={
            "child": child.id,
            "package": package.title,
            "finished_at": "202201010219",
            # "started_at": None
        }
    )

    assert resp.json()["ok"]

    resp = api_client.post(
        buy_package_url,
        data={
            "child": child.id,
            "package": package.title
        }
    )
    resp_data = resp.json()
    assert not resp_data["permissible"]
    assert resp_data["coin_remaining"] == 0
    assert resp_data["duration_remaining"] == 0
    assert resp_data["message"] == "no_coin"
