from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializes Review objects."""

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at',
        ]
        read_only_fields = ['reviewer']

    def validate(self, attrs):
        """Prevents the same reviewer from creating multiple reviews for the same business user (returns 403)."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            business_user = attrs.get('business_user')
            if Review.objects.filter(
                business_user=business_user,
                reviewer=request.user,
            ).exists():
                raise PermissionDenied(
                    "You have already submitted a review for this business user."
                )
        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializes Reviews for updates (PATCH); only rating and description are editable."""

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'business_user', 'reviewer', 'created_at', 'updated_at',
        ]