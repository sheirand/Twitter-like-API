from django.utils.functional import SimpleLazyObject
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, filters, exceptions, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from page.models import Page, Post
from page.permissions import AllowFollowers, IsOwnerOrStaff, ReadonlyIfPublic, PageBlocked, PageBasic, UserIsBanned
from page.serializers import PageSerializer, PostSerializer, FollowerSerializer, RequestSerializer, \
    PageExtendedSerializer, PostRepliesSerializer
from page.services import PageService, PostService


class PageAPIViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, PageBasic)
    queryset = Page.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title", "uniq_id", "tags__name",)

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return PageExtendedSerializer
        return PageSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(responses={
        202: '{"detail": "Your follow request is waiting to be accepted"}',
        201: '{"detail": "You now follow this page | You now longer follow this page"}'
    })
    @action(detail=True, methods=("GET",), url_path="follow", permission_classes=(IsAuthenticated,))
    def follow(self, request, pk, *args, **kwargs):
        page = self.get_object()
        msg = PageService.follow_unfollow_toggle(page, request)
        return Response(data=msg, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: FollowerSerializer})
    @action(detail=True, methods=("GET",), url_path="followers",
            serializer_class=FollowerSerializer, permission_classes=(IsOwnerOrStaff,))
    def followers(self, request, pk, *args, **kwargs):
        instance = self.get_queryset().get(id=pk)
        serializer = FollowerSerializer(instance=instance)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=FollowerSerializer)
    @action(detail=True, methods=("PATCH",), url_path="followers-remove",
            serializer_class=FollowerSerializer, permission_classes=(IsOwnerOrStaff,))
    def patch_followers(self, request, pk, *args, **kwargs):
        instance = self.get_queryset().get(id=pk)
        serializer = FollowerSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: RequestSerializer})
    @action(detail=True, methods=("GET",), url_path="follow-requests",
            serializer_class=RequestSerializer, permission_classes=(IsOwnerOrStaff,))
    def requests(self, request, pk, *args, **kwargs):
        instance = self.get_queryset().get(id=pk)
        serializer = RequestSerializer(instance=instance)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=RequestSerializer)
    @action(detail=True, methods=("PATCH",), url_path="approve-requests",
            serializer_class=RequestSerializer, permission_classes=(IsOwnerOrStaff,))
    def approve_requests(self, request, pk, *args, **kwargs):
        instance = self.get_queryset().get(id=pk)
        serializer = RequestSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostAPIViewset(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrStaff |
                          AllowFollowers | ReadonlyIfPublic |
                          UserIsBanned | PageBlocked)

    def get_queryset(self):
        return Post.objects.filter(page=self.kwargs.get('page_id'))

    def perform_create(self, serializer):
        serializer.save(page=Page.objects.get(pk=self.kwargs.get('page_id')), created_by=self.request.user)

    @swagger_auto_schema(responses={201: '{"detail": "You like this post | You dont like this post"}'})
    @action(detail=True, methods=("GET",), url_path='like-post-toggle')
    def like(self, request, pk, *args, **kwargs):
        post = self.get_object()
        msg = PostService.like_unlike_toggle(post, request)
        return Response(data=msg, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("GET",), url_path='replies')
    def replies(self, request, pk, *args, **kwargs):
        instance = PostService.get_visible_replies(pk)
        serializer = PostRepliesSerializer(instance=instance, many=True)
        return Response(serializer.data)


class FeedAPIViewset(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = PostSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("page__id", "page__uniq_id")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Post.objects.filter(page__followers=self.request.user.id,
                                   page__owner__is_blocked=False,
                                   page__is_blocked=False).order_by('-created_at')
