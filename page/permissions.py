from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from page.services import PageService


class IsOwnerOrStaff(permissions.BasePermission):
    """Return True if user is page owner or staff, False otherwise"""
    def has_permission(self, request, view):
        page = PageService.get_page_from_view(view)

        return (
                page.owner == request.user or
                request.user.is_staff
        )


class ReadonlyIfPublic(permissions.BasePermission):
    """Return True if page is public and
     HTTP methods are GET, HEAD or OPTION"""
    def has_permission(self, request, view):
        page = PageService.get_page_from_view(view)

        return (
                request.method in SAFE_METHODS and
                not page.is_private
        )


class AllowFollowers(permissions.BasePermission):
    """Return True if page is private and
     user is in page followers, False otherwise"""
    message = "Page is private"

    def has_permission(self, request, view):
        page = PageService.get_page_from_view(view)

        return (
                request.user in page.followers.all() and
                request.method in SAFE_METHODS
        )


class PageBlocked(permissions.BasePermission):
    """Return True if page is not blocked, False otherwise"""
    message = "Page is blocked"

    def has_permission(self, request, view):
        page = PageService.get_page_from_view(view)

        return not page.is_blocked


class PageBasic(permissions.BasePermission):
    """Return True if user is page owner or staff,
     otherwise allows only GET, HEAD, OPTION HTTP methods"""
    def has_object_permission(self, request, view, obj):

        return (
                request.method in SAFE_METHODS or
                obj.owner == request.user
                or request.user.is_staff
        )


class UserIsBanned(permissions.BasePermission):
    """Return False if user is banned, True otherwise"""

    def has_permission(self, request, view):
        page = PageService.get_page_from_view(view)

        return not page.owner.is_blocked
