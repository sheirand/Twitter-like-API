from rest_framework import serializers
from page.models import Page, User, Post, Tag


class PageExtendedSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())
    owner = serializers.SlugRelatedField(slug_field='email', read_only=True)
    followers = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)
    follow_requests = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)

    class Meta:
        model = Page
        fields = ("id", "uniq_id", "title", "description", "tags",
                  "owner", "followers", "image", "is_private",
                  "is_blocked", "follow_requests", "unblock_date")

    def to_internal_value(self, data):
        for tag_name in data.get('tags', []):
            Tag.objects.get_or_create(name=tag_name)
        return super().to_internal_value(data)


class PageSerializer(PageExtendedSerializer):
    class Meta:
        model = Page
        fields = ("id", "uniq_id", "title", "description", "tags",
                  "owner", "followers", "image", "is_private",
                  "is_blocked", "follow_requests", "unblock_date")
        read_only_fields = ("is_blocked", "unblock_date")


class PostSerializer(serializers.ModelSerializer):
    liked_by = serializers.SlugRelatedField(many=True, slug_field='email', read_only=True)
    created_by = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
        read_only_fields = ('id', 'page', 'created_at', 'updated_at')


class FollowerSerializer(serializers.ModelSerializer):
    followers = serializers.SlugRelatedField(many=True, slug_field="email",
                                             queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ("followers",)

    def update(self, instance, validated_data):
        users = validated_data.pop('followers')
        for user in users:
            instance.followers.remove(user)
        instance.save()
        return instance


class RequestSerializer(serializers.ModelSerializer):
    follow_requests = serializers.SlugRelatedField(many=True, slug_field="email",
                                                   queryset=User.objects.all())
    followers = serializers.SlugRelatedField(many=True, slug_field="email", read_only=True)

    class Meta:
        model = Post
        fields = ("follow_requests", "followers")

    def update(self, instance, validated_data):
        users = validated_data.pop('follow_requests')
        for user in users:
            instance.follow_requests.remove(user)
            instance.followers.add(user)
        instance.save()
        return instance


class PostRepliesSerializer(serializers.ModelSerializer):
    post = PostSerializer

    class Meta:
        model = Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
        read_only_fields = ('id', 'page', 'created_at', 'updated_at')
