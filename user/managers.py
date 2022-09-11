from django.contrib.auth.models import UserManager

from user.choises import Roles


class CustomUserManager(UserManager):
    def create_user(self, email: str, password: str, role: str = Roles.USER, is_blocked: bool = False) -> "User":
        if not email:
            raise ValueError("email is required")
        if not password:
            raise ValueError("password is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_blocked = is_blocked
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

