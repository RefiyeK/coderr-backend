from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderListSerializer(serializers.ModelSerializer):
    """Serialisiert Orders für die Listen-Ansicht (GET)."""

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at',
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serialisiert Orders für die Erstellung (POST) als Snapshot von einem OfferDetail."""
    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at',
            'offer_detail_id',
        ]
        read_only_fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price', 'features',
            'offer_type', 'status', 'created_at', 'updated_at',
        ]

    def validate_offer_detail_id(self, value):
        """Prüft, ob das angegebene OfferDetail existiert."""
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"OfferDetail mit id {value} existiert nicht.")
        return value

    def create(self, validated_data):
        """Erstellt eine neue Order als Snapshot vom angegebenen OfferDetail."""
        offer_detail_id = validated_data.pop('offer_detail_id')
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        order = Order.objects.create(
            customer_user=self.context['request'].user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )
        return order
