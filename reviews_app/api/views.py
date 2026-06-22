from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from reviews_app.models import Review
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from .filters import ReviewFilter
from .permissions import IsCustomerUserOrReadOnly, IsReviewerOrReadOnly


class ReviewListView(generics.ListCreateAPIView):
    """View for the reviews list (GET) and review creation (POST) at /api/reviews/."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']

    def perform_create(self, serializer):
        """Automatically sets the logged-in user as the reviewer."""
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for PATCH and DELETE of a Review at /api/reviews/<id>/."""
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrReadOnly]