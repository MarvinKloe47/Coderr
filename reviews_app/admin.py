from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("reviewer", "business_user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("reviewer__username", "business_user__username", "description")
    readonly_fields = ("created_at", "updated_at")
