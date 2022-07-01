from rest_framework import serializers
from page import models


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = "__all__"
