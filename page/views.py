from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from page.models import Page, Post
from page.permissions import AllowFollowers, IsOwnerOrStaff, ReadonlyIfPublic, PageBlocked, PageBasic
from page.serializers import PageSerializer, PostSerializer, FollowerSerializer, RequestSerializer


class PageAPIViewset(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated, PageBasic)
    queryset = Page.objects.all()

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_staff:
            queryset = Page.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=("POST",), url_path="follow", permission_classes=(IsAuthenticated,))
    def follow(self, request, pk):
        page = self.get_object()
        if page.is_private:
            page.follow_requests.add(request.user)
            return Response({"detail": "Your follow request is waiting to be accepted"}, status=200)
        page.followers.add(request.user)
        return Response({"detail": "Success"}, status=200)

    @action(detail=True, methods=("POST",), url_path="unfollow", permission_classes=(IsAuthenticated,))
    def unfollow(self, request, pk):
        page = self.get_object()
        page.followers.remove(request.user)
        return Response({"detail": "You are no longer follow this page"}, status=200)

    @action(detail=True, methods=("GET", "PUT", "PATCH",),
            url_path="followers", serializer_class=FollowerSerializer,
            permission_classes=(IsOwnerOrStaff,))
    def followers(self, request, pk):
        instance = self.get_queryset().get(id=pk)
        if request.method == "GET":
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data)
        serializer = self.get_serializer(instance=instance, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=("GET", "PUT", "PATCH",),
            url_path="follow_requests", serializer_class=RequestSerializer,
            permission_classes=(IsOwnerOrStaff,))
    def requests(self, request, pk):
        instance = self.get_queryset().get(id=pk)
        if request.method == "GET":
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data)
        serializer = self.get_serializer(instance=instance, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostAPIViewset(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrStaff | AllowFollowers | ReadonlyIfPublic | PageBlocked)

    def get_queryset(self):
        return Post.objects.filter(page=self.kwargs.get('page_id'))

    def perform_create(self, serializer):
        serializer.save(page=Page.objects.get(pk=self.kwargs.get('page_id')), created_by=self.request.user)

    @action(detail=True, methods=("POST",), url_path='like_post')
    def like(self, request, pk):
        post = self.get_object()
        post.liked_by.add(request.user)
        return Response({"detail": f"You like this post {pk} now"}, status=200)

    @action(detail=True, methods=("POST",), url_path='unlike_post')
    def unlike(self, request, pk):
        post = self.get_object()
        post.liked_by.remove(request.user)
        return Response({"detail": f"You took away your like from post {pk}"}, status=200)
