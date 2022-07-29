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
def another_user():
    payload = dict(
        email="harry_potter@hogwarts.com",
        password="flipendo"
    )
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
def another_user_token(client, another_user):

    response = client.post("/api/v1/user/login/", data={"email": another_user.email,
                                                        "password": "flipendo"})

    token = response.data["token"]

    return token


@pytest.fixture
def superuser_token(client, superuser):

    response = client.post("/api/v1/user/login/", data={"email": superuser.email,
                                                        "password": "thewitcher"})

    token = response.data["token"]

    return token


@pytest.fixture
def page_public():
    page = dict(
        title="Star Wars fandom",
        description="Hi there! Here we can discuss latest news about SW universe",
        tags=["SW", "jedi"],
        image="image-path/image.png",
        is_private=False
    )
    return page


@pytest.fixture
def another_private_page():
    page = dict(
        title="Harry Potter fans home",
        description="Hi there! Here we can discuss latest news about HP universe",
        tags=["HP"],
        image="image-path/image.png",
        is_private=True
    )

    return page


@pytest.fixture
def another_public_page():
    page = dict(
        title="World of warcraft",
        description="The place for all Azeroth warriors",
        tags=["WOW", "blizzard"],
        image="image-path/wow.jpg",
        is_private=False
    )

    return page


@pytest.fixture
def page_private(page_public):

    private_page = page_public.copy()
    private_page['is_private'] = True

    return private_page


@pytest.fixture
def page_blocked(page_public):

    blocked_page = page_public.copy()
    blocked_page['is_blocked'] = True

    return blocked_page


@pytest.fixture
def client_with_pages(client, user_token, superuser_token, another_user_token,
                      page_public, page_private, page_blocked, another_private_page,
                      another_public_page):

    client.post('/api/v1/pages/', page_public,
                HTTP_AUTHORIZATION=f"{user_token}", format='json')

    client.post('/api/v1/pages/', page_private,
                HTTP_AUTHORIZATION=f"{user_token}", format='json')

    client.post('/api/v1/pages/', page_blocked,
                HTTP_AUTHORIZATION=f"{superuser_token}", format='json')

    client.post('/api/v1/pages/', another_private_page,
                HTTP_AUTHORIZATION=f"{another_user_token}", format='json')

    client.post('/api/v1/pages/', another_public_page,
                HTTP_AUTHORIZATION=f"{another_user_token}", format='json')

    return client


@pytest.fixture
def page_ids(client_with_pages, superuser_token):

    response = client_with_pages.get('/api/v1/pages/',
                                     HTTP_AUTHORIZATION=f"{superuser_token}", format='json')

    public_page_id = response.data[0]['id']
    private_page_id = response.data[1]['id']
    blocked_page_id = response.data[2]['id']
    another_private_page_id = response.data[3]['id']
    another_public_page_id = response.data[4]['id']

    page_ids = dict(
        public_page_id=public_page_id,
        private_page_id=private_page_id,
        blocked_page_id=blocked_page_id,
        another_private_page_id=another_private_page_id,
        another_public_page_id=another_public_page_id
    )

    return page_ids


@pytest.fixture
def client_with_pages_and_followers(client_with_pages, user_token, page_ids):

    client_with_pages.get(f'/api/v1/pages/{page_ids["another_public_page_id"]}/follow/',
                          HTTP_AUTHORIZATION=f"{user_token}", format='json')

    client_with_pages.get(f'/api/v1/pages/{page_ids["another_private_page_id"]}/follow/',
                          HTTP_AUTHORIZATION=f"{user_token}", format='json')

    return client_with_pages
