from django.contrib import admin
from page import models


admin.site.register(models.Page)
admin.site.register(models.Post)
admin.site.register(models.Tag)
