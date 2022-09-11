from django.contrib import admin
from page import models
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("uniq_id", "title", "owner", "is_blocked")
    ordering = ("uniq_id",)
    list_filter = ("is_blocked", "is_private")
    search_fields = ("title", "uniq_id", "owner__email")
    filter_horizontal = ("tags", "followers", "follow_requests")


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "page", "created_at")
    list_display_links = ("id", "page")
    ordering = ("created_at",)
    search_fields = ("page__title",)


admin.site.register(models.Tag)
