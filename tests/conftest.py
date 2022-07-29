import pytest
from rest_framework.test import APIClient

from user.models import User
from user.choises import Roles


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
    payload = {
        "email": "harry_potter@hogwarts.com",
        "password": "flipendo"
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
        "role": Roles.MODERATOR
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
    payload = {
        "email": user,
        "password": "youshallnotpass"
    }
    response = client.post("/api/v1/user/login/", data=payload)
    token = response.data["token"]

    return token


@pytest.fixture
def another_user_token(client, another_user):
    payload = {
        "email": another_user,
        "password": "flipendo"
    }
    response = client.post("/api/v1/user/login/", data=payload)

    token = response.data["token"]

    return token


@pytest.fixture
def moderator_token(client, user_staff):
    payload = {
        "email": "luke_skywalker@starwars.com",
        "password": "forcebewithyou",
    }
    response = client.post("/api/v1/user/login/", data=payload)

    token = response.data["token"]

    return token


@pytest.fixture
def superuser_token(client, superuser):
    payload = {
        "email": superuser,
        "password": "thewitcher"
    }
    response = client.post("/api/v1/user/login/", data=payload)

    token = response.data["token"]

    return token


@pytest.fixture
def page_public():
    page = {
        "title": "Star Wars fandom",
        "description": "Hi there! Here we can discuss latest news about SW universe",
        "tags": ["SW", "jedi"],
        "image": "image-path/image.png",
        "is_private": False
    }

    return page


@pytest.fixture
def another_private_page():
    page = {
        "title": "Harry Potter fans home",
        "description": "Hi there! Here we can discuss latest news about HP universe",
        "tags": ["HP"],
        "image": "image-path/image.png",
        "is_private": True
    }

    return page


@pytest.fixture
def another_public_page():
    page = {
        "title": "World of warcraft",
        "description": "The place for all Azeroth warriors",
        "tags": ["WOW", "blizzard"],
        "image": "image-path/wow.jpg",
        "is_private": False
    }

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

    page_ids = {
        "public_page_id": public_page_id,
        "private_page_id": private_page_id,
        "blocked_page_id": blocked_page_id,
        "another_private_page_id": another_private_page_id,
        "another_public_page_id": another_public_page_id
    }

    return page_ids


@pytest.fixture
def client_with_pages_and_followers(client_with_pages, user_token, page_ids):

    client_with_pages.get(f'/api/v1/pages/{page_ids["another_public_page_id"]}/follow/',
                          HTTP_AUTHORIZATION=f"{user_token}", format='json')

    client_with_pages.get(f'/api/v1/pages/{page_ids["another_private_page_id"]}/follow/',
                          HTTP_AUTHORIZATION=f"{user_token}", format='json')

    return client_with_pages


@pytest.fixture
def first_post():
    post = {
        "content": "First post",
    }

    return post


@pytest.fixture
def client_with_first_post(client_with_pages_and_followers, user_token, page_ids, first_post):

    client_with_pages_and_followers.post(f"/api/v1/pages/{page_ids['public_page_id']}/posts/",
                                         data=first_post,
                                         HTTP_AUTHORIZATION=f"{user_token}",
                                         format='json')

    return client_with_pages_and_followers


@pytest.fixture
def first_post_id(client_with_first_post, user_token, page_ids):

    response = client_with_first_post.get(f"/api/v1/pages/{page_ids['public_page_id']}/posts/",
                                          HTTP_AUTHORIZATION=f"{user_token}")
    first_post_id = response.data[0]["id"]

    return first_post_id


@pytest.fixture
def any_other_post(first_post_id):
    post = {
        "content": "any other content",
        "reply_to": first_post_id
    }

    return post


@pytest.fixture
def demo_client(client_with_first_post, page_ids, user_token,
                another_user_token, superuser_token, any_other_post):

    client = client_with_first_post
    # posts on users public page
    client.post(f"/api/v1/pages/{page_ids['public_page_id']}/posts/",
                data=any_other_post,
                HTTP_AUTHORIZATION=f"{user_token}",
                format='json')

    # posts on another user's page
    client.post(f"/api/v1/pages/{page_ids['another_public_page_id']}/posts/",
                data=any_other_post,
                HTTP_AUTHORIZATION=f"{another_user_token}",
                format='json')
    client.post(f"/api/v1/pages/{page_ids['another_public_page_id']}/posts/",
                data=any_other_post,
                HTTP_AUTHORIZATION=f"{another_user_token}",
                format='json')
    # posts on private another user's page
    client.post(f"/api/v1/pages/{page_ids['another_private_page_id']}/posts/",
                data=any_other_post,
                HTTP_AUTHORIZATION=f"{another_user_token}",
                format='json')
    # posts on blocked page
    client.post(f"/api/v1/pages/{page_ids['blocked_page_id']}/posts/",
                data=any_other_post,
                HTTP_AUTHORIZATION=f"{superuser_token}",
                format='json')

    return client
