from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialisiert Review-Objekte."""

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at',
        ]