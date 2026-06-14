from rest_framework import generics
from rest_framework.permissions import AllowAny
from offers_app.models import Offer
from .serializers import OfferListSerializer


class OfferListView(generics.ListAPIView):
    """View für den Offer-List Endpoint (GET /api/offers/)."""
    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer
    permission_classes = [AllowAny]