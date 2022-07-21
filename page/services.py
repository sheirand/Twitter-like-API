from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist

from page.models import Page, Post


class PageService:

    @staticmethod
    def get_page_from_view(view):
        pk = view.kwargs.get('page_id')
        if not pk:
            pk = view.kwargs.get('pk')
        try:
            page = Page.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        return page

    @staticmethod
    def follow_unfollow_toggle(page, request) -> str:

        if request.user not in page.followers.all():
            if page.is_private:
                page.follow_requests.add(request.user)
                msg = "Your follow request is waiting to be accepted"
                return msg
            page.followers.add(request.user)
            msg = "You now follow this page"
            return msg
        page.followers.remove(request.user)
        msg = "You are no longer follow this page"
        return msg


class PostService:

    @staticmethod
    def get_visible_replies(pk):
        posts = Post.objects.filter(reply_to=pk, page__owner__is_blocked=False, page__is_blocked=False)
        if not posts:
            raise exceptions.NotFound()
        return posts

    @staticmethod
    def like_unlike_toggle(post, request) -> str:
        if request.user not in post.liked_by.all():
            post.liked_by.add(request.user)
            msg = "You like this post"
            return msg
        post.liked_by.remove(request.user)
        msg = "You dont like this post"
        return msg
