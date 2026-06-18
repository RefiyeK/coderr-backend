from rest_framework import serializers
from orders_app.models import Order


class OrderListSerializer(serializers.ModelSerializer):
    """Serialisiert Orders für die Listen-Ansicht (GET)."""

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at',
        ]