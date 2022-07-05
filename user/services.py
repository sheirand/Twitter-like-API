import datetime
import jwt

from django.conf import settings
from django.contrib.auth.models import UserManager
from user.choises import Roles


class CustomUserManager(UserManager):
    def create_user(self, email: str, password: str, role: str = Roles.USER) -> "User":
        if not email:
            raise ValueError("email is required")
        if not password:
            raise ValueError("password is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = True
        user.role = role
        if user.role == Roles.MODERATOR:
            user.is_staff = True
            user.is_superuser = False
            user.save()
            return user
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return user

    def create_superuser(self, email: str, password: str) -> "User":
        if not email:
            raise ValueError("email is required")
        if not password:
            raise ValueError("password is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = True
        user.role = Roles.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


def create_jwt_token(user_id: int, user_email: str) -> str:
    payload = dict(
        id=user_id,
        email=user_email,
        iat=datetime.datetime.utcnow(),
        exp=datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
    )
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    return token


REQUIRED_FIELDS = {
    "email": "This field is required",
    "password": "This field is required"
}
