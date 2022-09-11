from rest_framework import viewsets, views, permissions, filters, mixins
from rest_framework.permissions import AllowAny

from user.models import User
from user.permissions import IsOwnerOrAdmin
from user.serializers import UserSerializer, UserCredentialsSerializer, UserFullSerializer, UserTokenSerializer


class UserAPIViewset(viewsets.ModelViewSet):
    """API endpoint for User model"""
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("email",)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCredentialsSerializer
        else:
            if self.request.user.is_superuser:
                return UserFullSerializer
            return UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = (permissions.IsAdminUser,)
        elif self.action == 'create':
            permission_classes = (permissions.AllowAny,)
        else:
            permission_classes = (IsOwnerOrAdmin,)
        return [permission() for permission in permission_classes]


class UserLoginAPIViewset(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenSerializer
    queryset = User.objects.all()
