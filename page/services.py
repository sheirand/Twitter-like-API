from rest_framework import exceptions, status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

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
    def follow_unfollow_toggle(page, request):
        user = request.user

        if user not in page.followers.all():
            if page.is_private:
                page.follow_requests.add(user)
                return Response(data={"detail": "Your follow request is waiting to be accepted"},
                                status=status.HTTP_202_ACCEPTED)
            page.followers.add(user)
            return Response(data={"detail": "You now follow this page"},
                            status=status.HTTP_201_CREATED)
        page.followers.remove(user)
        return Response(data={"detail": "You are no longer follow this page"},
                        status=status.HTTP_201_CREATED)


class PostService:

    @staticmethod
    def get_visible_replies(pk):
        posts = Post.objects.filter(reply_to=pk, page__owner__is_blocked=False, page__is_blocked=False)
        if not posts:
            raise exceptions.NotFound()
        return posts

    @staticmethod
    def like_unlike_toggle(post, request):
        user = request.user
        if user not in post.liked_by.all():
            post.liked_by.add(user)
            return Response(data={"detail": "Your like this post"},
                            status=status.HTTP_201_CREATED)
        post.liked_by.remove(user)
        return Response(data={"detail": "You dont like this post"},
                        status=status.HTTP_201_CREATED)
