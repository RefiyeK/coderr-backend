from rest_framework import serializers
from offers_app.models import Offer, OfferDetail


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Kompakte Darstellung eines OfferDetails (nur ID + URL) für die Liste."""
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Erzeugt die relative URL zum OfferDetail."""
        return f'/offerdetails/{obj.id}/'


class OfferListSerializer(serializers.ModelSerializer):
    """Serialisiert Offers für die Listen-Ansicht."""
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details',
        ]

    def get_min_price(self, obj):
        """Liefert den niedrigsten Preis aller Details."""
        details = obj.details.all()
        if not details:
            return None
        return min(d.price for d in details)

    def get_min_delivery_time(self, obj):
        """Liefert die kürzeste Lieferzeit aller Details."""
        details = obj.details.all()
        if not details:
            return None
        return min(d.delivery_time_in_days for d in details)

    def get_user_details(self, obj):
        """Liefert grundlegende User-Daten als verschachteltes Objekt."""
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }