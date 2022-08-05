import pytest
from rest_framework.test import APIClient

from user.models import User


@pytest.fixture
def user():
    payload = {
        "email": "bilbo_baggins@shire.com",
        "password": "youshallnotpass",
    }

    user = User.objects.create_user(**payload)

    return user


@pytest.fixture
def blocked_user():
    payload = {
        "email": "talrasha@diablo.com",
        "password": "demoninside",
        "is_blocked": True
    }

    user = User.objects.create_user(**payload)

    return user


@pytest.fixture
def user_staff():
    payload = {
        "email": "luke_skywalker@starwars.com",
        "password": "forcebewithyou",
        "is_staff": True
    }

    user = User.objects.create_user(**payload)

    return user


@pytest.fixture
def superuser():
    payload = {
        "email": "geralt_of_rivia@neverland.com",
        "password": "thewitcher",
    }

    user = User.objects.create_superuser(**payload)

    return user


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_token(client, user):

    response = client.post("/api/v1/user/login/", data={"email": user.email,
                                                        "password": "youshallnotpass"})
    token = response.data["token"]

    return token


@pytest.fixture
def superuser_token(client, superuser):

    response = client.post("/api/v1/user/login/", data={"email": superuser.email,
                                                        "password": "thewitcher"})

    token = response.data["token"]

    return token
