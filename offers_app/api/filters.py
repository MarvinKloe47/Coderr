import django_filters
from django.db.models import Min

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    creator_id = django_filters.NumberFilter(field_name="user_id")
    max_delivery_time = django_filters.NumberFilter(method="filter_delivery_time")

    class Meta:
        model = Offer
        fields = ["creator_id", "max_delivery_time"]

    def filter_delivery_time(self, queryset, name, value):
        return queryset.annotate(
            lowest_delivery_time=Min("details__delivery_time_in_days")
        ).filter(lowest_delivery_time__lte=value)
