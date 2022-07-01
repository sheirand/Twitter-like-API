import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    uniq_id = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_("Page title"), max_length=80)
    description = models.TextField(_("Page description"))
    tags = models.ManyToManyField(Tag, related_name='pages')
    owner = models.ForeignKey(User, related_name='pages', on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='follows')
    image = models.URLField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField(User, related_name='requests')
    unblock_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=255)
    liked_by = models.ManyToManyField(User, related_name='likes')
    reply_to = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    updated_at = models.DateTimeField(auto_now=True)

