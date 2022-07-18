from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from page.models import Page, Post
from page.permissions import AllowFollowers, IsOwnerOrStaff, ReadonlyIfPublic, PageBlocked, PageBasic, UserIsBanned
from page.serializers import PageSerializer, PostSerializer, FollowerSerializer, RequestSerializer, \
    PageExtendedSerializer


class PageAPIViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, PageBasic)
    queryset = Page.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return PageExtendedSerializer
        return PageSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(responses={200: '{"detail": "Success!"}',
                                    202: '{"detail": "Your follow request is waiting to be accepted"}'})
    @action(detail=True, methods=("GET",), url_path="follow", permission_classes=(IsAuthenticated,))
    def follow(self, request, pk):
        page = self.get_object()
        if page.is_private:
            page.follow_requests.add(request.user)
            return Response({"detail": "Your follow request is waiting to be accepted"}, status=202)
        page.followers.add(request.user)
        return Response({"detail": "Success"}, status=200)

    @swagger_auto_schema(responses={200: '{"detail": "You are no longer follow this page"}'})
    @action(detail=True, methods=("GET",), url_path="unfollow", permission_classes=(IsAuthenticated,))
    def unfollow(self, request, pk):
        page = self.get_object()
        page.follow_requests.remove(request.user)
        page.followers.remove(request.user)
        return Response({"detail": "You are no longer follow this page"}, status=200)

    @swagger_auto_schema(method="GET", responses={200: FollowerSerializer})
    @swagger_auto_schema(method="PATCH", request_body=FollowerSerializer)
    @action(detail=True, methods=("GET", "PATCH",),
            url_path="followers", serializer_class=FollowerSerializer,
            permission_classes=(IsOwnerOrStaff,))
    def followers(self, request, pk):
        instance = self.get_queryset().get(id=pk)
        if request.method == "GET":
            serializer = FollowerSerializer(instance=instance)
            return Response(serializer.data)
        serializer = FollowerSerializer(instance=instance, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(method="GET", responses={200: RequestSerializer})
    @swagger_auto_schema(method="PATCH", request_body=RequestSerializer)
    @action(detail=True, methods=("PATCH", "GET"),
            url_path="follow_requests", serializer_class=RequestSerializer,
            permission_classes=(IsOwnerOrStaff,))
    def requests(self, request, pk):
        instance = self.get_queryset().get(id=pk)
        if request.method == "GET":
            serializer = RequestSerializer(instance=instance)
            return Response(serializer.data)
        serializer = RequestSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostAPIViewset(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, UserIsBanned, PageBlocked,
                          IsOwnerOrStaff | AllowFollowers | ReadonlyIfPublic)

    def get_queryset(self):
        return Post.objects.filter(page=self.kwargs.get('page_id'))

    def perform_create(self, serializer):
        serializer.save(page=Page.objects.get(pk=self.kwargs.get('page_id')), created_by=self.request.user)

    @swagger_auto_schema(responses={200: '{"detail": "You like this post {%pk%} now"}'})
    @action(detail=True, methods=("GET",), url_path='like_post')
    def like(self, request, pk):
        post = self.get_object()
        post.liked_by.add(request.user)
        return Response({"detail": f"You like this post {pk} now"}, status=200)

    @swagger_auto_schema(responses={200: '{"detail": "You took away your like from post post {%pk%}"}'})
    @action(detail=True, methods=("GET",), url_path='unlike_post')
    def unlike(self, request, pk):
        post = self.get_object()
        post.liked_by.remove(request.user)
        return Response({"detail": f"You took away your like from post {pk}"}, status=200)
