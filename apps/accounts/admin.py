from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class StalingramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Профиль Stalingram", {"fields": ("bio", "avatar")}),
    )
