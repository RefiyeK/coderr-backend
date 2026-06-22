from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from profile_app.models import Profile
from profile_app.api.permissions import IsOwnerOrReadOnly
from profile_app.api.serializers import (
    ProfileDetailSerializer,
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
)


class ProfileDetailView(RetrieveUpdateAPIView):
    """View for the Profile detail endpoint (GET/PATCH /api/profile/{pk}/)."""

    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """Retrieves the Profile by user ID and checks object-level permissions."""
        profile = get_object_or_404(Profile, user_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, profile)
        return profile


class BusinessProfileListView(generics.ListAPIView):
    """Lists all profiles of type 'business'."""
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filters profiles to users of type 'business'."""
        return Profile.objects.filter(user__type='business')


class CustomerProfileListView(generics.ListAPIView):
    """Lists all profiles of type 'customer'."""
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filters profiles to users of type 'customer'."""
        return Profile.objects.filter(user__type='customer')