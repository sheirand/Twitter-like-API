from rest_framework import serializers
from page import models


class PageSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=models.Tag.objects.all())
    owner = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = models.Page
        fields = ("id", "uniq_id", "title", "description", "tags",
                  "owner", "followers", "image", "is_private",
                  "is_blocked", "follow_requests", "unblock_date")
        extra_kwargs = {
                "owner": {'read_only': True},
                "followers": {'read_only': True},
                "follow_requests": {'read_only': True},
                "is_blocked": {'read_only': True},
                "unblock_date": {'read_only': True},
        }

    def to_internal_value(self, data):
        for tag_name in data.get('tags', []):
            models.Tag.objects.get_or_create(name=tag_name)
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
