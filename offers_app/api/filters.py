import django_filters
from django.db.models import Min

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Apply documented query parameters to public offer lists.

    Creator filtering uses the offer owner directly, while price and delivery
    filters compare against each offer's best package values.
    """

    creator_id = django_filters.NumberFilter(field_name="user_id")
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_delivery_time = django_filters.NumberFilter(method="filter_delivery_time")

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]

    def filter_min_price(self, queryset, name, value):
        """Filter by the lowest package price of each offer."""
        return queryset.annotate(lowest_price=Min("details__price")).filter(
            lowest_price__gte=value
        )

    def filter_delivery_time(self, queryset, name, value):
        """Filter by the fastest package delivery time of each offer."""
        return queryset.annotate(
            lowest_delivery_time=Min("details__delivery_time_in_days")
        ).filter(lowest_delivery_time__lte=value)
