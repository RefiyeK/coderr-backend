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
    """View for the orders list (GET) and order creation (POST) at /api/orders/."""
    permission_classes = [IsCustomerUserOrReadOnly]

    def get_queryset(self):
        """Returns only orders in which the logged-in user is involved."""
        return Order.objects.filter(
            Q(customer_user=self.request.user) | Q(
                business_user=self.request.user)
        )

    def get_serializer_class(self):
        """Selects the appropriate serializer based on the HTTP method."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for PATCH and DELETE of an Order at /api/orders/<id>/."""
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer

    def get_permissions(self):
        """Selects permissions based on the HTTP method."""
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated(), IsBusinessOwnerForUpdate()]


class OrderCountView(APIView):
    """View for the number of in-progress orders of a business user at /api/order-count/<business_user_id>/."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Returns the number of orders with status 'in_progress' for the given business user."""
        if not CustomUser.objects.filter(id=business_user_id, type='business').exists():
            return Response(
                {'detail': 'Business user not found.'},
                status=http_status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress'
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """View for the number of completed orders of a business user at /api/completed-order-count/<business_user_id>/."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Returns the number of orders with status 'completed' for the given business user."""
        if not CustomUser.objects.filter(id=business_user_id, type='business').exists():
            return Response(
                {'detail': 'Business user not found.'},
                status=http_status.HTTP_404_NOT_FOUND,
            )
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed'
        ).count()
        return Response({'completed_order_count': count})