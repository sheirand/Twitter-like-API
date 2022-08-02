from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from page.services import PageService


class IsOwnerOrStaff(permissions.BasePermission):
    """Return True if user is page owner or staff, False otherwise"""
    def has_permission(self, request, view):
        page = PageService.get_page_from_kwargs(view.kwargs)

        return (
                page.owner == request.user or
                request.user.is_staff
        )


class AllowFollowers(permissions.BasePermission):
    """Return True if page is private and
     user is in page followers, False otherwise"""
    message = "Page is private"

    def has_permission(self, request, view):
        page = PageService.get_page_from_kwargs(view.kwargs)

        return (
                request.method in SAFE_METHODS and
                (request.user in page.followers.all() or not page.is_private)
        )


class PageBlocked(permissions.BasePermission):
    """Return True if page is not blocked, False otherwise"""
    message = "Page is blocked"

    def has_permission(self, request, view):
        page = PageService.get_page_from_kwargs(view.kwargs)

        return not page.is_blocked and not page.owner.is_blocked


class PageBasic(permissions.BasePermission):
    """Return True if user is page owner or staff,
     otherwise allows only GET, HEAD, OPTION HTTP methods"""
    def has_object_permission(self, request, view, obj):

        return (
                request.method in SAFE_METHODS or
                obj.owner == request.user
                or request.user.is_staff
        )
