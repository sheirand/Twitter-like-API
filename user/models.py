from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_user(self, email: str, password: str, role: str = "user") -> "User":
        if not email:
            raise ValueError("email is required")
        if not password:
            raise ValueError("password is required")
        if role not in ["user", "moderator"]:
            raise ValueError("role must be either \"moderator\" or \"user\"")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = True
        user.role = role
        if user.role == "moderator":
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
        user.role = "admin"
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"
    first_name = None
    last_name = None
    username = None
    email = models.EmailField(_("email"), max_length=150, unique=True)
    image_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices)
    is_blocked = models.BooleanField(
        _("blocked"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site.")
    )
    blocked_to = models.DateTimeField(_("blocked until:"), null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]
