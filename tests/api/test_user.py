import pytest
from django.conf import settings

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
import jwt


@pytest.mark.django_db
def test_register_user(client):

    payload = {
        "email": "old_hobbit@shire.com",
        "password": "youshallnotpass"
    }

    response = client.post("/api/v1/user/", payload)

    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data["role"] == "user"
    assert data["email"] == payload["email"]
    assert "password" not in data


@pytest.mark.django_db
def test_user_login(client, user):

    payload = {
        "email": user,
        "password": "youshallnotpass"
    }

    response = client.post("/api/v1/user/login/", data=payload)

    credentials = jwt.decode(response.data["token"],
                             settings.JWT_SECRET_KEY,
                             algorithms=['HS256'])

    assert response.status_code == status.HTTP_201_CREATED
    assert "token" in response.data
    assert user.email == credentials["email"]
    assert user.id == credentials["id"]


@pytest.mark.django_db
def test_blocked_user_cant_login(client, blocked_user):

    payload = {
        "email": blocked_user,
        "password": "demoninsideme"
    }

    response = client.post("/api/v1/user/login/", data=payload)

    data = response.data

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "token" not in data
    assert data['detail'] == "This user is blocked permanently"


@pytest.mark.django_db
def test_get_user_info_by_superuser(client, user, superuser_token):

    response = client.get(f"/api/v1/user/{user.id}/", {},
                          HTTP_AUTHORIZATION=f"{superuser_token}")

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert data["role"] == user.role
    assert data["email"] == user.email
    assert data["id"] == user.id


@pytest.mark.django_db
def test_access_user_endpoint_by_user(client, user, user_token):

    response = client.get(f"/api/v1/user/{user.id}/", {},
                          HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert data["role"] == user.role
    assert data["email"] == user.email


@pytest.mark.django_db
def test_access_forbidden_another_user_detail(client, superuser, user_token):

    response = client.get(f"/api/v1/user/{superuser.id}/", {},
                          HTTP_AUTHORIZATION=f"{user_token}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_change_profile(client, user, user_token):
    payload = {"image_path": "path/image.jpg"}

    response = client.patch(f"/api/v1/user/{user.id}/",
                            data=payload,
                            HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert data["image_path"] == payload["image_path"]


@pytest.mark.django_db
def superuser_can_change_user_profile(client, user, superuser_token):
    payload = {
        "id": user.id,
        "email": user.email,
        "role": "moderator",
        "image_path": "path/image.jpg",
        "is_blocked": True,
        "blocked_to": "2023-09-12"
    }

    response = client.put(f"/api/v1/user/{user.id}/",
                          data=payload,
                          HTTP_AUTHORIZATION=f"{superuser_token}")

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == payload["id"]
    assert data["email"] == payload["email"]
    assert data["role"] == payload["role"]
    assert data["image_path"] == payload["image_path"]
    assert data["is_blocked"] == payload["is_blocked"]
    assert data["blocked_to"] == payload["blocked_to"]


@pytest.mark.django_db
def test_user_delete(client, user, superuser_token):

    response = client.delete(f"/api/v1/user/{user.id}/", {},
                             HTTP_AUTHORIZATION=f"{superuser_token}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(ObjectDoesNotExist):
        user.refresh_from_db()
