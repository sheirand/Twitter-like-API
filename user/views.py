from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import mixins
from user.models import User
from user.serializers import UserSerializer


class UserAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLoginAPIView(views.APIView):
    def get(self, request):
        return Response({"detail": "Email and password fields is required"}, status=200)

    def post(self, request):
        return Response({"detail": "NOT IMPLEMENTED YET"})


class UserLogoutAPIView(views.APIView):
    def post(self, request):
        return Response({"detail": "NOT IMPLEMENTED YET"})


class UserProfileAPIView(mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
