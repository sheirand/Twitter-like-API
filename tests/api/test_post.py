import pytest
from django.core.exceptions import ObjectDoesNotExist
from pytest_django.asserts import assertNumQueries
from rest_framework import status
from page.models import Post


@pytest.mark.django_db
def test_get_posts_on_his_page(demo_client, user, user_token, page_ids, any_other_post):
    with assertNumQueries(8):
        response = demo_client.get(f"/api/v1/pages/{page_ids['public_page_id']}/posts/",
                                   HTTP_AUTHORIZATION=f"{user_token}")

    data = response.data[1]

    assert response.status_code == status.HTTP_200_OK
    assert data["content"] == any_other_post["content"]
    assert data["reply_to"] == any_other_post["reply_to"]
    assert data["created_by"]['email'] == user.email
