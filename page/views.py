from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from page.models import Page, Post
from page.permissions import AllowFollowers, IsOwnerOrStaff, ReadonlyIfPublic
from page.serializers import PageSerializer, PostSerializer, FollowerSerializer


class PageAPIViewset(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Page.objects.all()
        return Page.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=("POST",), url_path="follow-page")
    def follow(self, request, pk):
        page = self.get_object()
        if page.is_private:
            page.follow_requests.add(request.user)
            return Response({"detail": "Your follow request is waiting to be accepted"}, status=200)
        page.followers.add(request.user)
        return Response({"detail": "Success"}, status=200)

    @action(detail=True, methods=("POST",), url_path="unfollow-page")
    def unfollow(self, request, pk):
        page = self.get_object()
        page.followers.remove(request.user)
        return Response({"detail": "You are no longer follow this page"}, status=200)

    @action(detail=True, methods=("GET", "PUT", "PATCH",),
            url_path="get-followers", serializer_class=FollowerSerializer)
    def followers(self, request, pk):
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
    permission_classes = (IsAuthenticated, IsOwnerOrStaff | AllowFollowers | ReadonlyIfPublic)

    def get_queryset(self):
        return Post.objects.filter(page=self.kwargs.get('page_id'))

    def perform_create(self, serializer):
        serializer.save(page=Page.objects.get(pk=self.kwargs.get('page_id')), created_by=self.request.user)

    @action(detail=True, methods=("POST",), url_path='like-post')
    def like(self, request, pk):
        post = self.get_object()
        post.liked_by.add(request.user)
        return Response({"detail": f"You like this post {pk} now"}, status=200)

    @action(detail=True, methods=("POST",), url_path='unlike-post')
    def unlike(self, request, pk):
        post = self.get_object()
        post.liked_by.remove(request.user)
        return Response({"detail": f"You took away your like from post {pk}"}, status=200)
