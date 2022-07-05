from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm
from django.contrib.auth.admin import Group
from user import models


class UserCreationForm(ModelForm):
    class Meta:
        model = models.User
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    list_display = ("email", 'role', 'is_blocked')
    ordering = ("email",)
    list_filter = ("role", "is_blocked")
    search_fields = ("email",)
    fieldsets = (
        (None, {'fields': ('email', 'role', 'is_blocked', 'blocked_to', 'image_path')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'role', 'is_blocked', 'blocked_to', 'image_path')}
         ),
    )

    filter_horizontal = ()


admin.site.register(models.User, CustomUserAdmin)
admin.site.unregister(Group)
