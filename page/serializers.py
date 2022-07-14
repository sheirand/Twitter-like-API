from rest_framework import serializers
from page.models import Page, User, Post, Tag


class PageSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())
    owner = serializers.SlugRelatedField(slug_field='email', read_only=True)
    followers = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)
    follow_requests = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)

    class Meta:
        model = Page
        fields = ("id", "uniq_id", "title", "description", "tags",
                  "owner", "followers", "image", "is_private",
                  "is_blocked", "follow_requests", "unblock_date")
        extra_kwargs = {
                "unblock_date": {'read_only': True},
        }

    def to_internal_value(self, data):
        for tag_name in data.get('tags', []):
            Tag.objects.get_or_create(name=tag_name)
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    page = serializers.SlugRelatedField(slug_field='title', read_only=True)
    liked_by = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)
    created_by = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
        extra_kwargs = {
            "read_only_fields": ('id', 'created_at', 'updated_at')
        }


class FollowerSerializer(serializers.ModelSerializer):
    followers = serializers.SlugRelatedField(many=True, slug_field="email",
                                             queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ("followers",)


class RequestSerializer(serializers.ModelSerializer):
    follow_requests = serializers.SlugRelatedField(many=True, slug_field="email",
                                                   queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ("follow_requests",)

    def update(self, instance, validated_data):
        users = validated_data.pop('follow_requests')
        for user in users:
            instance.followers.add(user)
        instance.save()
        return instance
