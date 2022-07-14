import datetime
import traceback

import jwt

from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser
from user.models import User


class JWTService:

    @staticmethod
    def create_jwt_token(user_id: int, user_email: str) -> str:
        """Service for creating jwt"""
        payload = dict(
            id=user_id,
            email=user_email,
            iat=datetime.datetime.utcnow(),
            exp=datetime.datetime.utcnow() + datetime.timedelta(minutes=40)
        )
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

        return token

    @staticmethod
    def get_jwt_user(request) -> "User":
        """Service for get user by jwt in request headers"""
        user_jwt = get_user(request)
        if user_jwt.is_authenticated:
            return user_jwt

        token = request.headers.get('Authorization', None)
        user_jwt = AnonymousUser()

        if token is not None:
            try:
                user_jwt = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=['HS256']
                )
                user_jwt = User.objects.get(
                    id=user_jwt['id']
                )

            except Exception as e:
                traceback.print_exc()

        return user_jwt
