import django_filters
from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    """Filter für Reviews nach business_user_id und reviewer_id."""
    business_user_id = django_filters.NumberFilter(field_name='business_user')
    reviewer_id = django_filters.NumberFilter(field_name='reviewer')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']