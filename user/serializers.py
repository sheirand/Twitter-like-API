from rest_framework import serializers
from user import models


class UserFullSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = ("id", "email", "role", "image_path", "is_blocked", "blocked_to")


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    is_blocked = serializers.BooleanField(read_only=True)
    blocked_to = serializers.DateTimeField(read_only=True)

    class Meta:
        model = models.User
        fields = ("id", "email", "role", "image_path", "is_blocked", "blocked_to")


class UserCredentialsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(raw_password=password)
        user.save()
        return user

    class Meta:
        model = models.User
        fields = ("id", "email", "password", "role")
