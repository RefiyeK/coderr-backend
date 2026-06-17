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


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialisiert OfferDetails für die Erstellung, Bearbeitung und Anzeige."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serialisiert Offers für die Erstellung und Bearbeitung."""
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """Erstellt ein Offer mit seinen Details."""
        details_data = validated_data.pop('details')
        validated_data['user'] = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def validate_details(self, value):
        """Validiert, dass genau 3 Details übergeben werden."""
        if len(value) != 3:
            raise serializers.ValidationError(
                "Ein Angebot muss genau 3 Details haben.")
        return value


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


class OfferRetrieveSerializer(OfferListSerializer):
    """Serialisiert ein einzelnes Offer für die Detail-Ansicht (ohne user_details)."""

    class Meta(OfferListSerializer.Meta):
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time',
        ]


class OfferUpdateSerializer(OfferCreateSerializer):
    """Serialisiert Offers für die Aktualisierung (ähnlich wie Create)."""

    def validate_details(self, value):
        """Bei PATCH dürfen 1 bis 3 Details übergeben werden, jeder offer_type nur einmal."""
        if len(value) < 1 or len(value) > 3:
            raise serializers.ValidationError(
                "Es müssen zwischen 1 und 3 Details angegeben werden.")

        types = [d['offer_type'] for d in value]
        if len(types) != len(set(types)):
            raise serializers.ValidationError(
                "Jeder offer_type darf nur einmal vorkommen.")
        return value

    def update(self, instance, validated_data):
        """Aktualisiert ein Offer und seine Details (Nested Update)."""
        details_data = validated_data.pop('details', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for detail_data in details_data:
            offer_type = detail_data.pop('offer_type')
            detail_instance = instance.details.get(offer_type=offer_type)
            for attr, value in detail_data.items():
                setattr(detail_instance, attr, value)
            detail_instance.save()
        return instance
