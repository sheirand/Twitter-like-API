from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from page.models import Page, Post
from page.permissions import AllowFollowers, IsOwnerOrStaff, ReadonlyIfPublic
from page.serializers import PageSerializer, PostSerializer


class PageAPIViewset(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)

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


class PostAPIViewset(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(page=self.kwargs.get('page_id'))

    def perform_create(self, serializer):
        serializer.save(page=Page.objects.get(pk=self.kwargs.get('page_id')))

#    permission_classes = (IsOwnerOrStaff | AllowFollowers | ReadonlyIfPublic,)
