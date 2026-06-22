from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Min

from offers_app.models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer, OfferCreateSerializer, OfferRetrieveSerializer,
    OfferUpdateSerializer, OfferDetailSerializer,
)
from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessUserOrReadOnly, IsOwnerOrReadOnly


class OfferListView(generics.ListCreateAPIView):
    """View for the offers list (GET) and offer creation (POST) at /api/offers/."""
    queryset = Offer.objects.all().annotate(
        min_price=Min('details__price')
    ).order_by('-updated_at').distinct()
    serializer_class = OfferListSerializer
    permission_classes = [IsBusinessUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['min_price', 'updated_at']
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    pagination_class = OfferPagination

    def get_serializer_class(self):
        """Selects the appropriate serializer based on the HTTP method."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for detail (GET), update (PATCH) and deletion (DELETE) of an Offer at /api/offers/<id>/."""
    queryset = Offer.objects.all()
    serializer_class = OfferRetrieveSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """Selects the appropriate serializer based on the HTTP method."""
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """View for the detail of an OfferDetail at /api/offerdetails/<id>/."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]