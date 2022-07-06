from rest_framework import serializers
from user import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(raw_password=password)
        user.save()
        return user

    class Meta:
        model = models.User
        fields = ("id", "email", "password", "role", "image_path", "is_blocked", "blocked_to")


class UserLoginSerializer(UserSerializer):
    class Meta:
        model = models.User
        fields = ("email", "password")
