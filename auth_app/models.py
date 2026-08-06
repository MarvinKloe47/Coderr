from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Create Coderr users while preserving Django password handling.

    The manager requires usernames, normalizes email addresses and assigns the
    business role to superusers so admin accounts satisfy the custom user model.
    """

    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create regular users with normalized email and hashed password."""
        if not username:
            raise ValueError("The username must be set.")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create admin users with required staff flags and a business role."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("type", User.Types.BUSINESS)
        if not extra_fields.get("is_staff") or not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have staff and superuser flags.")
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Store authentication data plus Coderr profile and role fields.

    The single type field distinguishes customer and business users throughout
    serializers, permissions, profile lists, offers, orders and reviews.
    """

    class Types(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    type = models.CharField(max_length=20, choices=Types.choices)
    file = models.ImageField(upload_to="profiles/", blank=True, null=True)
    tel = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username
