from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status

from orders_app.models import Order
from .serializers import OrderListSerializer, OrderCreateSerializer, OrderUpdateSerializer
from .permissions import IsCustomerUserOrReadOnly, IsBusinessOwnerForUpdate
from auth_app.models import CustomUser


class OrderListView(generics.ListCreateAPIView):
    """View für die Order-Liste (GET) und Order-Erstellung (POST) unter /api/orders/."""
    permission_classes = [IsCustomerUserOrReadOnly]

    def get_queryset(self):
        """Liefert nur Orders zurück, an denen der eingeloggte User beteiligt ist."""
        return Order.objects.filter(
            Q(customer_user=self.request.user) | Q(
                business_user=self.request.user)
        )

    def get_serializer_class(self):
        """Wählt den passenden Serializer abhängig von der HTTP-Methode."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View für PATCH und DELETE einer Order unter /api/orders/<id>/."""
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer

    def get_permissions(self):
        """Wählt Permissions abhängig von der HTTP-Methode."""
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated(), IsBusinessOwnerForUpdate()]


class OrderCountView(APIView):
    """View für die Anzahl laufender Orders eines Business-Users unter /api/order-count/<business_user_id>/."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Liefert die Anzahl der Orders mit Status 'in_progress' für den angegebenen Business-User."""
        if not CustomUser.objects.filter(id=business_user_id, type='business').exists():
            return Response(
                {'detail': 'Business-User nicht gefunden.'},
                status=http_status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress'
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """View für die Anzahl abgeschlossener Orders eines Business-Users unter /api/completed-order-count/<business_user_id>/."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Liefert die Anzahl der Orders mit Status 'completed' für den angegebenen Business-User."""
        if not CustomUser.objects.filter(id=business_user_id, type='business').exists():
            return Response(
                {'detail': 'Business-User nicht gefunden.'},
                status=http_status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed'
        ).count()
        return Response({'completed_order_count': count})