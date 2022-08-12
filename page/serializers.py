from rest_framework import serializers

from page.models import Page, User, Post, Tag
from page.services import StatsService
from user.serializers import NestedUserSerializer


class PageExtendedSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())
    owner = NestedUserSerializer(read_only=True)
    followers = NestedUserSerializer(many=True, read_only=True)
    follow_requests = NestedUserSerializer(many=True, read_only=True)

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
    liked_by = NestedUserSerializer(many=True, read_only=True)
    created_by = NestedUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
        read_only_fields = ('id', 'page', 'created_at', 'updated_at')


class FollowerSerializer(serializers.ModelSerializer):
    followers = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ("followers",)

    def update(self, instance, validated_data):
        users = validated_data.pop('followers')
        for user in users:
            instance.followers.remove(user)
        # publish data to stats microservice
        StatsService.publish_remove_followers(page_id=validated_data.pop("id"),
                                              num=len(users))
        instance.save()
        return instance


class RequestSerializer(serializers.ModelSerializer):
    follow_requests = serializers.PrimaryKeyRelatedField(many=True,
                                                         queryset=User.objects.all())
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("follow_requests", "followers")

    def update(self, instance, validated_data):
        users = validated_data.pop('follow_requests')
        for user in users:
            instance.follow_requests.remove(user)
            instance.followers.add(user)
        # publish data to stats microservice
        StatsService.publish_new_followers(page_id=validated_data.pop("id"),
                                           num=len(users))
        instance.save()
        return instance


class PostRepliesSerializer(serializers.ModelSerializer):
    liked_by = NestedUserSerializer(many=True, read_only=True)
    created_by = NestedUserSerializer(read_only=True)
    reply_to = PostSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "page", "content", "liked_by", "reply_to",
                  "created_at", "created_by", "updated_at",)
        read_only_fields = ('id', 'page', 'created_at', 'updated_at')
