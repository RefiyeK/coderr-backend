from rest_framework import serializers
from offers_app.models import Offer, OfferDetail


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Compact representation of an OfferDetail (only ID + URL) for list views."""
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Builds the relative URL to the OfferDetail."""
        return f'/offerdetails/{obj.id}/'


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializes OfferDetails for creation, update and display."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializes Offers for creation."""
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """Creates an Offer along with its details."""
        details_data = validated_data.pop('details')
        validated_data['user'] = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def validate_details(self, value):
        """Validates that exactly 3 details are provided."""
        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must have exactly 3 details.")
        return value


class OfferListSerializer(serializers.ModelSerializer):
    """Serializes Offers for the list view."""
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
        """Returns the lowest price among all details."""
        details = obj.details.all()
        if not details:
            return None
        return min(d.price for d in details)

    def get_min_delivery_time(self, obj):
        """Returns the shortest delivery time among all details."""
        details = obj.details.all()
        if not details:
            return None
        return min(d.delivery_time_in_days for d in details)

    def get_user_details(self, obj):
        """Returns basic user data as a nested object."""
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }


class OfferRetrieveSerializer(OfferListSerializer):
    """Serializes a single Offer for the detail view (excludes user_details)."""

    class Meta(OfferListSerializer.Meta):
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time',
        ]


class OfferUpdateSerializer(OfferCreateSerializer):
    """Serializes Offers for updates (PATCH); allows 1-3 details with unique offer_types."""

    def validate_details(self, value):
        """In PATCH, 1 to 3 details may be provided; each must include offer_type, and each offer_type can appear only once."""
        if len(value) < 1 or len(value) > 3:
            raise serializers.ValidationError(
                "Between 1 and 3 details must be provided.")

        types = []
        for detail in value:
            if 'offer_type' not in detail:
                raise serializers.ValidationError(
                    "Each detail must include 'offer_type' to identify which package to update.")
            types.append(detail['offer_type'])

        if len(types) != len(set(types)):
            raise serializers.ValidationError(
                "Each offer_type may appear only once.")
        return value

    def update(self, instance, validated_data):
        """Updates an Offer and its details (nested update)."""
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