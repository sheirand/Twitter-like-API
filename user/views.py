from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, views, exceptions, permissions
from rest_framework.response import Response

from user import services
from user.models import User
from user.permissions import IsOwnerOrAdmin
from user.serializers import UserSerializer, UserCredentialsSerializer, UserFullSerializer


class UserAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()

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
    @swagger_auto_schema(request_body=UserCredentialsSerializer,
                         operation_description="Returns JWT if credentials were provided",
                         responses={200: "Success. Returns JSON: {\"jwt:\" \"token\"}",
                                    403: "Forbidden. Invalid credentials"}
                         )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            raise exceptions.ValidationError(detail=services.REQUIRED_FIELDS)

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        token = services.create_jwt_token(user_id=user.id, user_email=user.email)

        resp = Response({"jwt_token": token}, status=200)

        return resp
