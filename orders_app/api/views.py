from rest_framework import generics
from django.db.models import Q

from orders_app.models import Order
from .serializers import OrderListSerializer, OrderCreateSerializer
from .permissions import IsCustomerUserOrReadOnly


class OrderListView(generics.ListCreateAPIView):
    """View für die Order-Liste (GET) und Order-Erstellung (POST) unter /api/orders/."""
    permission_classes = [IsCustomerUserOrReadOnly]

    def get_queryset(self):
        """Liefert nur Orders zurück, an denen der eingeloggte User beteiligt ist."""
        return Order.objects.filter(
            Q(customer_user=self.request.user) | Q(business_user=self.request.user)
        )

    def get_serializer_class(self):
        """Wählt den passenden Serializer abhängig von der HTTP-Methode."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer