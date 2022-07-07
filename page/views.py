from rest_framework import viewsets
from page.models import Page, Post
from page.serializers import PageSerializer, PostSerializer


class PageAPIView(viewsets.ModelViewSet):
    serializer_class = PageSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Page.objects.all()
        return Page.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostAPIView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
