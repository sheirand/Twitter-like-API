import datetime
import pytz
import jwt

from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions

from user import models
from user.models import User

import logging

logger = logging.getLogger(__name__)
utc = pytz.UTC


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

            except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError) as error:
                logger.error(f"JWT error message: {error}")
                raise exceptions.AuthenticationFailed(error)

        return user_jwt


class UserService:

    @staticmethod
    def authenticate(email: str = None, password: str = None) -> "User":

        user = models.User.objects.get(email=email)

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        if not UserService.check_ban_status(user):
            raise exceptions.NotAuthenticated(
                f"This user is blocked till {user.blocked_to.strftime('%d/%m/%y %H:%M')}"
            )

        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        if not user.is_active:
            raise exceptions.NotAuthenticated(
                'This user has been deactivated.'
            )

        return user

    @staticmethod
    def check_ban_status(user):
        """Service for unbanning user
        Return True if user ban expired or
        user is not banned, False otherwise"""
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        ban_end = user.blocked_to
        if ban_end:
            ban_end.replace(tzinfo=utc)
        if user.is_blocked and not ban_end:
            raise exceptions.NotAuthenticated(
                f"This user is blocked permanently"
            )

        if user.is_blocked and now > ban_end:
            user.is_blocked = False
            user.blocked_to = None
            user.save()
            return True

        return not user.is_blocked
