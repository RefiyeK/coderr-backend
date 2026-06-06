from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from profile_app.api.permissions import IsOwnerOrReadOnly

from profile_app.models import Profile
from .serializers import ProfileDetailSerializer


class ProfileDetailView(RetrieveUpdateAPIView):
    """View für den Profile-Detail Endpoint (GET/PATCH /api/profile/{pk}/)."""

    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """Holt das Profile per User-ID und prüft Objektberechtigungen."""
        profile = get_object_or_404(Profile, user_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, profile)
        return profile