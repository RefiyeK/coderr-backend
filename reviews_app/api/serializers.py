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
        read_only_fields = ['reviewer']

    def validate(self, attrs):
        """Verhindert, dass derselbe Reviewer mehrere Reviews für denselben Business-User erstellt."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            business_user = attrs.get('business_user')
            if Review.objects.filter(
                business_user=business_user,
                reviewer=request.user,
            ).exists():
                raise serializers.ValidationError(
                    "Du hast diesem Business-User bereits eine Bewertung gegeben."
                )
        return attrs
    
class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serialisiert Reviews für die Aktualisierung (PATCH) - nur rating und description."""

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'business_user', 'reviewer', 'created_at', 'updated_at',
        ]