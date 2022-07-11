from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from page.models import Page, Post
from page.permissions import IsFollowerOrOwnerOrStaff
from page.serializers import PageSerializer, PostSerializer, FollowerSerializer
from user.models import User


class PageAPIView(viewsets.ModelViewSet):
    serializer_class = PageSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Page.objects.all()
        return Page.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=("POST",))
    def follow(self, request, pk):
        page = self.get_object()
        if page.is_private:
            page.follow_requests.add(request.user)
            return Response({"detail": "Your follow request is waiting to be accepted"}, status=200)
        page.followers.add(request.user)
        return Response({"detail": "Success"}, status=200)

    @action(detail=True, methods=("POST",))
    def unfollow(self, request, pk):
        page = self.get_object()
        page.followers.remove(request.user)
        return Response({"detail": "You are no longer follow this page"}, status=200)


class PostAPIView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsFollowerOrOwnerOrStaff,)