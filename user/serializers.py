from rest_framework import serializers
from user import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "email", "password", "role", "image_path", "is_blocked", "blocked_to"]