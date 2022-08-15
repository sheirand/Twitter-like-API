from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail
from core.producer import PikaClient

from page.models import Page, Post


class PageService:

    @staticmethod
    def get_page_from_kwargs(kwargs: dict):
        pk = kwargs.get('page_id')
        if not pk:
            pk = kwargs.get('pk')
        try:
            page = Page.objects.prefetch_related('followers').\
                select_related('owner').get(id=pk)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        return page

    @staticmethod
    def follow_unfollow_toggle(page, request) -> dict:

        if request.user not in page.followers.all():
            if page.is_private:
                page.follow_requests.add(request.user)
                msg = {"detail": "Your follow request is waiting to be accepted"}
                return msg
            page.followers.add(request.user)
            msg = {"detail": "You now follow this page"}
            # publish data to stats microservice
            StatsService.publish_new_followers(page.id)
            return msg
        page.followers.remove(request.user)
        msg = {"detail": "You are no longer follow this page"}
        # publish data to stats microservice
        StatsService.publish_remove_followers(page.id)
        return msg


class PostService:

    @staticmethod
    def get_visible_replies(pk):
        posts = Post.objects.filter(reply_to=pk, page__owner__is_blocked=False, page__is_blocked=False).\
            prefetch_related("liked_by", "reply_to__liked_by").\
            select_related("page", "reply_to", "created_by", "reply_to__created_by", "reply_to__page")
        if not posts:
            raise exceptions.NotFound()
        return posts

    @staticmethod
    def like_unlike_toggle(request, pk, post) -> dict:
        if not Post.objects.filter(id=pk, liked_by=request.user).exists():
            post.liked_by.add(request.user)
            msg = {"detail": "You like this post"}
            StatsService.publish_like(post.page.id)
            return msg
        post.liked_by.remove(request.user)
        msg = {"detail": "You dont like this post"}
        StatsService.publish_unlike(post.page.id)
        return msg

    @staticmethod
    def send_email(emails_list: list, msg: str):
        """ Email notification for new post on followed page"""
        send_mail(
            "Notification from Innotter!",
            msg,
            settings.EMAIL_HOST_USER,
            emails_list,
            fail_silently=False
        )


class StatsService:
    """Service for producing messages to Stats microservice"""

    __client = PikaClient()

    @staticmethod
    def publish_page_creation(page_id, user_id):
        data = {"id": page_id,
                "user_id": user_id}
        StatsService.__client.publish("page created", data)

    @staticmethod
    def publish_new_followers(page_id, num=1):
        data = {"id": page_id, "num": num}
        StatsService.__client.publish("add followers", data)

    @staticmethod
    def publish_remove_followers(page_id, num=1):
        data = {"id": page_id, "num": num}
        StatsService.__client.publish("remove followers", data)

    @staticmethod
    def publish_post_creation(page_id):
        data = {"id": page_id}
        StatsService.__client.publish("new post", data)

    @staticmethod
    def publish_like(page_id):
        data = {"id": page_id}
        StatsService.__client.publish("like", data)

    @staticmethod
    def publish_unlike(page_id):
        data = {"id": page_id}
        StatsService.__client.publish("unlike", data)

    @staticmethod
    def publish_page_delete(page_id):
        data = {"id": page_id}
        StatsService.__client.publish("page deleted", data)
