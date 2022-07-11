from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from page.models import Page


class IsFollowerOrOwnerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        page = Page.objects.filter(id=view.kwargs.get('pk')).first()
        if request.method in SAFE_METHODS and not page.is_private:
            return True
        return bool(page.owner == request.user or request.user.is_staff)


class IsOwnerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        page = Page.objects.filter(id=view.kwargs.get('pk')).first()
        return bool(page.owner == request.user or
                    request.user.is_staff
                    )


class IsFollowerOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        page = Page.objects.filter(id=view.kwargs.get('pk')).first()
        return bool(
            request.method in SAFE_METHODS and
            not page.is_private
        )

