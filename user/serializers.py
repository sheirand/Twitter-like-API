from rest_framework import serializers, exceptions
from user import models
from user.services import JWTService


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


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, max_length=128)
    token = serializers.CharField(read_only=True, max_length=255)

    def validate(self, data):
        """
        Validates user data.
        """
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = models.User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        token = JWTService.create_jwt_token(user_id=user.id, user_email=user.email)

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        if user.is_blocked:
            raise serializers.ValidationError(
                f"This user is blocked till {user.blocked_to.strftime('%d/%m/%y %H:%M')}"
            )

        return {
            'token': token,
        }
