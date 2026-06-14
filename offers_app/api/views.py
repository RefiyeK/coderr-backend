from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from offers_app.models import Offer
from .serializers import OfferListSerializer
from .filters import OfferFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Min
from .pagination import OfferPagination


class OfferListView(generics.ListAPIView):
    """View für den Offer-List Endpoint (GET /api/offers/)."""
    queryset = Offer.objects.all().annotate(
        min_price=Min('details__price')
        ).order_by('-updated_at').distinct()
    serializer_class = OfferListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['min_price', 'updated_at']
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    pagination_class = OfferPagination
