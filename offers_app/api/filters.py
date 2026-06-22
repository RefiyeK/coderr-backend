import django_filters
from django.db.models import Min

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Filters offers by creator_id, min_price, and max_delivery_time."""
    creator_id = django_filters.NumberFilter(field_name='user')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_delivery_time = django_filters.NumberFilter(
        method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_min_price(self, queryset, name, value):
        """Returns offers whose annotated min_price is greater than or equal to value."""
        return queryset.filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """Returns offers whose shortest delivery time is less than or equal to value."""
        return queryset.annotate(
            min_delivery=Min('details__delivery_time_in_days')
        ).filter(min_delivery__lte=value)