import pytest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from page.models import Page


@pytest.mark.django_db
def test_user_create_page(client, user_token, page_public):
    response = client.post('/api/v1/pages/', page_public,
                           HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_201_CREATED

    data = response.data

    assert data["title"] == page_public["title"]
    assert data["description"] == page_public["description"]
    assert data["tags"] == page_public["tags"]
    assert data["is_private"] == page_public["is_private"]


@pytest.mark.django_db
def test_user_get_pages(client_with_pages, user_token, page_public):
    response = client_with_pages.get('/api/v1/pages/',
                                     HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data[0]

    assert data["title"] == page_public["title"]
    assert data["description"] == page_public["description"]
    assert data["tags"] == page_public["tags"]
    assert data["is_private"] == page_public["is_private"]


@pytest.mark.django_db
def test_user_retrieve_pages(client_with_pages, page_ids, user_token,
                             page_public, page_private, page_blocked):
    response = client_with_pages.get(f'/api/v1/pages/{page_ids["public_page_id"]}/',
                                     HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert data['title'] == page_public['title']
    assert data['description'] == page_public['description']
    assert data['is_private'] == page_public['is_private']

    response = client_with_pages.get(f'/api/v1/pages/{page_ids["private_page_id"]}/',
                                     HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert data['title'] == page_private['title']
    assert data['description'] == page_private['description']
    assert data['is_private'] == page_private['is_private']

    response = client_with_pages.get(f'/api/v1/pages/{page_ids["blocked_page_id"]}/',
                                     HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert data['title'] == page_blocked['title']
    assert data['description'] == page_blocked['description']
    assert data['is_private'] == page_blocked['is_private']
    assert data['is_blocked'] == page_blocked['is_blocked']


@pytest.mark.django_db
def test_user_can_change_page(client_with_pages, page_ids, user_token):
    payload = dict(
        image="image-path/image.jpg"
    )

    response = client_with_pages.patch(f'/api/v1/pages/{page_ids["public_page_id"]}/',
                                       data=payload, HTTP_AUTHORIZATION=f"{user_token}",
                                       format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert data['image'] == payload["image"]


@pytest.mark.django_db
def test_user_cant_change_another_user_page(client_with_pages, page_ids, user_token):
    response = client_with_pages.patch(f'/api/v1/pages/{page_ids["another_private_page_id"]}/',
                                       data={"image": "image.jpeg"},
                                       HTTP_AUTHORIZATION=f"{user_token}",
                                       format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_delete_his_page(client_with_pages, page_ids, user_token):
    page = Page.objects.get(id=page_ids["public_page_id"])

    response = client_with_pages.delete(f'/api/v1/pages/{page_ids["public_page_id"]}/',
                                        HTTP_AUTHORIZATION=f"{user_token}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(ObjectDoesNotExist):
        page.refresh_from_db()


@pytest.mark.django_db
def test_superuser_can_block_page(client_with_pages, page_ids, superuser_token):
    payload = dict(
        is_blocked=True
    )

    response = client_with_pages.patch(f'/api/v1/pages/{page_ids["public_page_id"]}/',
                                       data=payload,
                                       HTTP_AUTHORIZATION=f"{superuser_token}",
                                       format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert data["is_blocked"] == payload["is_blocked"]


@pytest.mark.django_db
def test_user_can_follow_public_page(client_with_pages, user, user_token, page_ids):
    response = client_with_pages.get(f'/api/v1/pages/{page_ids["another_public_page_id"]}/follow/',
                                     HTTP_AUTHORIZATION=f"{user_token}")

    assert response.status_code == status.HTTP_201_CREATED

    data = response.data

    assert data["detail"] == "You now follow this page"
    assert Page.objects.filter(id=page_ids["another_public_page_id"],
                               followers=user).exists()


@pytest.mark.django_db
def test_user_can_follow_private_page(client_with_pages, user_token, page_ids, user):

    response = client_with_pages.get(f'/api/v1/pages/{page_ids["another_private_page_id"]}/follow/',
                                     HTTP_AUTHORIZATION=f"{user_token}")

    assert response.status_code == status.HTTP_201_CREATED

    data = response.data

    assert data["detail"] == "Your follow request is waiting to be accepted"
    assert Page.objects.filter(id=page_ids["another_private_page_id"],
                               follow_requests=user).exists()


@pytest.mark.django_db
def test_user_can_see_followers(client_with_pages_and_followers, another_user_token, page_ids, user):

    response = client_with_pages_and_followers.get(f'/api/v1/pages/{page_ids["another_public_page_id"]}/followers/',
                                                   HTTP_AUTHORIZATION=f"{another_user_token}")

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert user.id in data["followers"]


@pytest.mark.django_db
def test_user_can_see_follow_requests(client_with_pages_and_followers, another_user_token, page_ids, user):

    response = client_with_pages_and_followers.get(
        f'/api/v1/pages/{page_ids["another_private_page_id"]}/follow-requests/',
        HTTP_AUTHORIZATION=f"{another_user_token}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert user.id in data["follow_requests"]


@pytest.mark.django_db
def test_user_can_remove_followers(client_with_pages_and_followers, another_user_token, page_ids, user):
    payload = dict(
        followers=[user.id]
    )

    response = client_with_pages_and_followers.patch(
        f'/api/v1/pages/{page_ids["another_public_page_id"]}/followers-remove/',
        data=payload,
        HTTP_AUTHORIZATION=f"{another_user_token}",
        format='json'
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert user.id not in data["followers"]


@pytest.mark.django_db
def test_user_can_accept_follow_requests(client_with_pages_and_followers, another_user_token,
                                         page_ids, user):

    payload = dict(
        follow_requests=[user.id]
    )

    response = client_with_pages_and_followers.patch(
        f'/api/v1/pages/{page_ids["another_private_page_id"]}/approve-requests/',
        payload,
        HTTP_AUTHORIZATION=f"{another_user_token}",
        format='json'
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert user.id not in data["follow_requests"]
    assert user.id in data["followers"]
