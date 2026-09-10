from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class StalingramUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Профиль Stalingram", {"fields": ("bio", "avatar", "last_seen_at")}),
        ("Настройки Stalingram", {"fields": ("theme", "enter_to_send")}),
    )
    readonly_fields = ("last_seen_at",)
