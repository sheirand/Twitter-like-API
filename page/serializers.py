from rest_framework import serializers
from page import models


class PageSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=models.Tag.objects.all())
    owner = serializers.SlugRelatedField(slug_field='email', read_only=True)
    followers = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)
    follow_requests = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)

    class Meta:
        model = models.Page
        fields = ("id", "uniq_id", "title", "description", "tags",
                  "owner", "followers", "image", "is_private",
                  "is_blocked", "follow_requests", "unblock_date")
        extra_kwargs = {
                "is_blocked": {'read_only': True},
                "unblock_date": {'read_only': True},
        }

    def to_internal_value(self, data):
        for tag_name in data.get('tags', []):
            models.Tag.objects.get_or_create(name=tag_name)
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    page = serializers.SlugRelatedField(slug_field='title', read_only=True)
    liked_by = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)

    class Meta:
        model = models.Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
        extra_kwargs = {
            "id": {'read_only': True},
            "created_at": {'read_only': True},
            "created_by": {'read_only': True},
            "updated_at": {'read_only': True},
        }


class FollowerSerializer(serializers.ModelSerializer):
    followers = serializers.SlugRelatedField(many=True, slug_field='email', queryset=models.User.objects.all())

    class Meta:
        model = models.Post
        fields = ("followers",)

