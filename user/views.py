from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, views, exceptions, permissions, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from user.models import User
from user.permissions import IsOwnerOrAdmin
from user.serializers import UserSerializer, UserCredentialsSerializer, UserFullSerializer, UserTokenSerializer
from user.services import check_ban_status


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


class UserLoginAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenSerializer

    def post(self, request):
        """
        Checks if user exists.
        Email and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
