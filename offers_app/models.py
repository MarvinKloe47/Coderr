from django.conf import settings
from django.db import models


class Offer(models.Model):
    """Represent a service offer owned by a business user.

    Each offer groups the title, description and image shared by its three
    package details and is ordered by the latest update for list endpoints.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to="offers/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "id"]

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """Store one priced package tier for an offer.

    The basic, standard and premium tiers are unique per offer and are resolved
    by offer_type during nested offer updates.
    """

    class Types(models.TextChoices):
        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=120)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=Types.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_detail_type",
            )
        ]
        ordering = ["offer_id", "offer_type"]

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"
