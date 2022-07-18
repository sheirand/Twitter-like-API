from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS

from page.models import Page


class IsOwnerOrStaff(permissions.BasePermission):
    """Return True if user is page owner or staff, False otherwise"""
    def has_permission(self, request, view):
        pk = view.kwargs.get('page_id')
        if not pk:
            pk = view.kwargs.get('pk')
        page = Page.objects.filter(id=pk).first()
        if not page:
            raise exceptions.NotFound()

        return bool(page.owner == request.user or
                    request.user.is_staff
                    )


class ReadonlyIfPublic(permissions.BasePermission):
    """Return True if page is public and
     HTTP methods are GET, HEAD or OPTION"""
    def has_permission(self, request, view):
        pk = view.kwargs.get('page_id')
        if not pk:
            pk = view.kwargs.get('pk')
        page = Page.objects.filter(id=pk).first()
        if not page:
            raise exceptions.NotFound()
        return bool(
            request.method in SAFE_METHODS and
            not page.is_private
        )


class AllowFollowers(permissions.BasePermission):
    """Return True if page is private and
     user is in page followers, False otherwise"""
    message = "Page is private"

    def has_permission(self, request, view):
        pk = view.kwargs.get('page_id')
        if not pk:
            pk = view.kwargs.get('pk')
        page = Page.objects.filter(id=pk).first()
        if not page:
            raise exceptions.NotFound()
        return bool(
            request.user in page.followers.all() and
            request.method in SAFE_METHODS
        )


class PageBlocked(permissions.BasePermission):
    """Return True if page is not blocked, False otherwise"""
    message = "Page is blocked"

    def has_permission(self, request, view):
        pk = view.kwargs.get('page_id')
        if not pk:
            pk = view.kwargs.get('pk')
        page = Page.objects.filter(id=pk).first()
        if not page:
            raise exceptions.NotFound()
        return bool(
            not page.is_blocked and
            not request.user.is_staff
        )


class PageBasic(permissions.BasePermission):
    """Return True if user is page owner or staff,
     otherwise allows only GET, HEAD, OPTION HTTP methods"""
    def has_object_permission(self, request, view, obj):
        return bool(
             request.method in SAFE_METHODS or
             obj.owner == request.user
             or request.user.is_staff
        )


class UserIsBanned(permissions.BasePermission):
    """Return False if user is banned, True otherwise"""

    def has_permission(self, request, view):
        pk = view.kwargs.get('page_id')
        if not pk:
            pk = view.kwargs.get('pk')
        page = Page.objects.filter(id=pk).first()
        if not page:
            raise exceptions.NotFound()
        return not page.owner.is_blocked
