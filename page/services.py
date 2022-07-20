from rest_framework import exceptions, status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from page.models import Page


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
                return Response(status=status.HTTP_204_NO_CONTENT)
            page.followers.add(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        page.followers.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
