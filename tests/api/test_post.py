import pytest
from django.core.exceptions import ObjectDoesNotExist
from pytest_django.asserts import assertNumQueries
from rest_framework import status

from page.models import Post


@pytest.mark.django_db
def test_user_get_posts_on_his_page(demo_client, user, user_token, page_ids, any_other_post):

    response = demo_client.get(f"/api/v1/pages/{page_ids['public_page_id']}/posts/",
                               HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data[1]

    assert response.status_code == status.HTTP_200_OK
    assert data["content"] == any_other_post["content"]
    assert data["reply_to"] == any_other_post["reply_to"]
    assert data["created_by"]['email'] == user.email


@pytest.mark.django_db
def test_user_get_posts_on_followed_page(demo_client, user, user_token,
                                         another_user_token, page_ids,
                                         any_other_post, another_user):
    payload = {
        "follow_requests": [user.id]
    }
    # approve follow request before check
    demo_client.patch(f'/api/v1/pages/{page_ids["another_private_page_id"]}/approve-requests/',
                      data=payload,
                      HTTP_AUTHORIZATION=f"{another_user_token}",
                      format='json')

    response = demo_client.get(f"/api/v1/pages/{page_ids['another_private_page_id']}/posts/",
                               HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data[0]

    assert response.status_code == status.HTTP_200_OK
    assert data["content"] == any_other_post["content"]
    assert data["reply_to"] == any_other_post["reply_to"]
    assert data["created_by"]["email"] == another_user.email


@pytest.mark.django_db
def test_user_cant_get_posts_on_private_page(demo_client, user_token, page_ids):

    response = demo_client.get(f"/api/v1/pages/{page_ids['another_private_page_id']}/posts/",
                               HTTP_AUTHORIZATION=f"{user_token}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_create_post_on_his_page(demo_client, user, user_token, page_ids, any_other_post):

    response = demo_client.post(f"/api/v1/pages/{page_ids['private_page_id']}/posts/",
                                data=any_other_post,
                                HTTP_AUTHORIZATION=f"{user_token}",
                                format='json')

    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data['content'] == any_other_post["content"]
    assert data["reply_to"] == any_other_post["reply_to"]
    assert data["created_by"]["email"] == user.email
    assert data["page"] == page_ids["private_page_id"]


@pytest.mark.django_db
def test_user_cant_create_post_on_other_page(demo_client, user_token, page_ids, any_other_post):
    response = demo_client.post(f"/api/v1/pages/{page_ids['another_public_page_id']}/posts/",
                                data=any_other_post,
                                HTTP_AUTHORIZATION=f"{user_token}",
                                format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_detail_post(demo_client, user, user_token, page_ids, first_post, first_post_id):

    response = demo_client.get(f"/api/v1/pages/{page_ids['public_page_id']}/posts/{first_post_id}/",
                               HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert data["created_by"]["email"] == user.email
    assert data["page"] == page_ids["public_page_id"]


@pytest.mark.django_db
def test_user_can_change_his_post(demo_client, user, user_token, page_ids, first_post, first_post_id):
    payload = {
        "content": "new_content"
    }

    response = demo_client.patch(f"/api/v1/pages/{page_ids['public_page_id']}/posts/{first_post_id}/",
                                 data=payload,
                                 HTTP_AUTHORIZATION=f"{user_token}",
                                 format='json')

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert data["created_by"]["email"] == user.email
    assert data["page"] == page_ids["public_page_id"]
    assert data['content'] == payload["content"]


@pytest.mark.django_db
def test_user_can_delete_his_post(demo_client, user, user_token, page_ids, first_post, first_post_id):

    post = Post.objects.get(id=first_post_id)

    response = demo_client.delete(f"/api/v1/pages/{page_ids['public_page_id']}/posts/{first_post_id}/",
                                  HTTP_AUTHORIZATION=f"{user_token}", format='json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(ObjectDoesNotExist):
        post.refresh_from_db()


@pytest.mark.django_db
def test_user_can_like_post(demo_client, any_other_post_id, user_token, page_ids):
    url = f"/api/v1/pages/{page_ids['another_public_page_id']}/posts/{any_other_post_id}/like-post-toggle/"

    response = demo_client.get(url, HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data["detail"] == "You like this post"


@pytest.mark.django_db
def test_user_can_remove_like_post(demo_client, any_other_post_id, user_token, page_ids):
    url = f"/api/v1/pages/{page_ids['another_public_page_id']}/posts/{any_other_post_id}/like-post-toggle/"

    # like the post first
    demo_client.get(url, HTTP_AUTHORIZATION=f"{user_token}")

    response = demo_client.get(url, HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data["detail"] == "You dont like this post"


@pytest.mark.django_db
def test_user_can_see_replies(demo_client, first_post_id, user_token, page_ids):
    url = f"/api/v1/pages/{page_ids['public_page_id']}/posts/{first_post_id}/replies/"

    response = demo_client.get(url, HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == Post.objects.filter(reply_to=first_post_id, page__is_blocked=False).count()


@pytest.mark.django_db
def test_user_cant_see_posts_on_blocked_page(demo_client, user_token, page_ids):
    url = f"/api/v1/pages/{page_ids['blocked_page_id']}/posts/"

    response = demo_client.get(url, HTTP_AUTHORIZATION=f"{user_token}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == "Page is blocked"


@pytest.mark.django_db
def test_user_cant_post_posts_on_blocked_page(demo_client, user_token, moderator_token, page_ids, any_other_post):
    url = f"/api/v1/pages/{page_ids['public_page_id']}/posts/"
    payload = {
        "is_blocked": True
    }
    # block user's page by admin first
    demo_client.patch(f"/api/v1/pages/{page_ids['public_page_id']}/", data=payload,
                      HTTP_AUTHORIZATION=f"{moderator_token}", format='json')

    response = demo_client.post(url, data=any_other_post,
                                HTTP_AUTHORIZATION=f"{user_token}",
                                format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == "Page is blocked"
