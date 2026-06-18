from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import OrderListSerializer

from orders_app.models import Order
# from .serializers import OrderSerializer  ← şimdilik yorum, henüz yok


class OrderListView(generics.ListCreateAPIView):
    """View für die Order-Liste (GET) und Order-Erstellung (POST) unter /api/orders/."""
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Liefert nur Orders zurück, an denen der eingeloggte User beteiligt ist."""
        return Order.objects.filter(
            Q(customer_user=self.request.user) | Q(business_user=self.request.user)
        )
        