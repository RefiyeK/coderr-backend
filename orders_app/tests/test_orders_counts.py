from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from orders_app.models import Order


class OrderCountTests(APITestCase):
    """Tests für die Count-Endpoints (/api/order-count/, /api/completed-order-count/)."""

    def setUp(self):
        """Erstellt Customer, Business und Orders mit verschiedenen Stati."""
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        for status_value in ['in_progress', 'in_progress', 'completed', 'cancelled']:
            Order.objects.create(
                customer_user=self.customer,
                business_user=self.business,
                title='Logo Design',
                revisions=3, delivery_time_in_days=5, price=150,
                features=['Logo'], offer_type='basic',
                status=status_value,
            )

    def test_order_count_returns_in_progress_count(self):
        """Liefert die Anzahl der Orders mit Status 'in_progress' (200)."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-count', args=[self.business.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'order_count': 2})

    def test_completed_order_count_returns_completed_count(self):
        """Liefert die Anzahl der Orders mit Status 'completed' (200)."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('completed-order-count', args=[self.business.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'completed_order_count': 1})

    def test_order_count_for_nonexistent_business_returns_404(self):
        """Eine Anfrage für einen nicht existierenden Business-User gibt 404 zurück."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-count', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_for_nonexistent_business_returns_404(self):
        """Eine Anfrage für completed-order-count mit ungültiger ID gibt 404 zurück."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('completed-order-count', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_access_order_count(self):
        """Ein nicht authentifizierter User erhält 401 beim Abrufen von order-count."""
        url = reverse('order-count', args=[self.business.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_access_completed_order_count(self):
        """Ein nicht authentifizierter User erhält 401 beim Abrufen von completed-order-count."""
        url = reverse('completed-order-count', args=[self.business.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)