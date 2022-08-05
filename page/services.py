from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail

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
            return msg
        page.followers.remove(request.user)
        msg = {"detail": "You are no longer follow this page"}
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
    def like_unlike_toggle(request, pk, post) -> str:
        if not Post.objects.filter(id=pk, liked_by=request.user).exists():
            post.liked_by.add(request.user)
            msg = {"detail": "You like this post"}
            return msg
        post.liked_by.remove(request.user)
        msg = {"detail": "You dont like this post"}
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
