from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from page.models import Page


class IsOwnerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        page = Page.objects.filter(id=view.kwargs.get('page_id')).first()
        return bool(page.owner == request.user or
                    request.user.is_staff
                    )


class ReadonlyIfPublic(permissions.BasePermission):
    def has_permission(self, request, view):
        page = Page.objects.filter(id=view.kwargs.get('page_id')).first()
        return bool(
            request.method in SAFE_METHODS and
            not page.is_private
        )


class AllowFollowers(permissions.BasePermission):
    def has_permission(self, request, view):
        page = Page.objects.filter(id=view.kwargs.get('page_id')).first()
        return bool(
            request.user in page.followers.all() and
            request.method in SAFE_METHODS
        )
