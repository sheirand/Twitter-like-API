from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from user.choises import Roles
from user.services import CustomUserManager


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    email = models.EmailField(_("email"), max_length=150, unique=True)
    image_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices, default=Roles.USER)
    is_blocked = models.BooleanField(
        _("blocked"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site.")
    )
    blocked_to = models.DateTimeField(_("blocked until:"), null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    def __str__(self):
        return self.email
