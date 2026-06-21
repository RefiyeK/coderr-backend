from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from reviews_app.models import Review
from .serializers import ReviewSerializer
from .filters import ReviewFilter


class ReviewListView(generics.ListAPIView):
    """View für die Review-Liste (GET) unter /api/reviews/."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']