import pytest
from rest_framework import status


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
def test_user_get_public_pages(client_with_pages, user_token, page_public):

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

