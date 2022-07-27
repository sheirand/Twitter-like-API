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
def test_user_retrieve_public_page(client_with_pages, user_token, page_public):

    response = client_with_pages.get('/api/v1/pages/', HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_200_OK

    data = response.data[0]

    assert data["title"] == page_public["title"]
    assert data["description"] == page_public["description"]
    assert data["tags"] == page_public["tags"]
    assert data["is_private"] == page_public["is_private"]
