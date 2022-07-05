from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, views, exceptions
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from user import services
from user.models import User
from user.serializers import UserSerializer, UserLoginSerializer


class UserAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLoginAPIView(views.APIView):
    @swagger_auto_schema(request_body=UserLoginSerializer,
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


class UserProfileAPIView(mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
