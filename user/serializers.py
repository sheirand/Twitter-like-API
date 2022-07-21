from rest_framework import serializers

from user import models
from user.services import JWTService, UserService


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


class UserTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, max_length=128, required=True)
    token = serializers.CharField(read_only=True, max_length=255)

    class Meta:
        model = models.User
        fields = ("email", "password", "token")

    def validate(self, data):
        """
        Validates user data.
        """
        email = data.get('email')
        password = data.get('password')

        user = UserService.authenticate(email=email, password=password)

        data['user'] = user

        return data

    def create(self, validated_data):
        user = validated_data['user']
        token = JWTService.create_jwt_token(user_id=user.id, user_email=user.email)
        return {"token": token}

