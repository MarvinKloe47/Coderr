from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Expose Coderr profile fields in Django's built-in user admin."""

    fieldsets = UserAdmin.fieldsets + (
        (
            "Coderr profile",
            {
                "fields": (
                    "type",
                    "file",
                    "tel",
                    "location",
                    "description",
                    "working_hours",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Coderr role", {"fields": ("type", "email")}),
    )
    list_display = ("username", "email", "type", "is_staff", "created_at")
    list_filter = ("type", "is_staff", "is_active")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("username", "email", "first_name", "last_name")
