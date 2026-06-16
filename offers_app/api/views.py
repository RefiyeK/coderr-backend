from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Min

from offers_app.models import Offer
from .serializers import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer
from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessUserOrReadOnly, IsOwnerOrReadOnly


class OfferListView(generics.ListCreateAPIView):
    """View für die Offer-Liste (GET) und Offer-Erstellung (POST) unter /api/offers/."""
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
        """Wählt den passenden Serializer abhängig von der HTTP-Methode."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer


class OfferDetailView(generics.RetrieveDestroyAPIView):
    """View für Detail-Ansicht (GET) und Löschung (DELETE) eines Offers unter /api/offers/<id>/."""
    queryset = Offer.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
