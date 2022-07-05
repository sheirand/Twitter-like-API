from rest_framework import viewsets
from page.models import Page, Post
from page.serializers import PageSerializer, PostSerializer


class PageAPIView(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class PostAPIView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
