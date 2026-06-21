from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import CustomUser
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    """View für allgemeine Plattform-Statistiken unter /api/base-info/."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Liefert Anzahl Reviews, durchschnittliches Rating, Business-Profile und Offers."""
        average = Review.objects.aggregate(avg=Avg('rating'))['avg']
        return Response({
            'review_count': Review.objects.count(),
            'average_rating': round(average, 1) if average is not None else 0.0,
            'business_profile_count': CustomUser.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count(),
        })