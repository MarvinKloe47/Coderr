from django.contrib import admin

from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Edit offer package tiers inside the parent offer admin page."""

    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Manage offers together with their nested package details."""

    inlines = [OfferDetailInline]
    list_display = ("title", "user", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Inspect and search individual offer package tiers in the admin."""

    list_display = ("title", "offer", "offer_type", "price", "delivery_time_in_days")
    list_filter = ("offer_type",)
    search_fields = ("title", "offer__title")
