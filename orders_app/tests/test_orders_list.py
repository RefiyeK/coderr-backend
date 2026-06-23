from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from orders_app.models import Order


class OrderListTests(APITestCase):
    """Tests for the order list endpoint (GET /api/orders/)."""

    def setUp(self):
        """Creates two customers, two business users, and several orders."""
        self.customer_a = CustomUser.objects.create_user(
            username='customer_a', email='ca@coderr.de',
            password='testpass123', type='customer',
        )
        self.customer_b = CustomUser.objects.create_user(
            username='customer_b', email='cb@coderr.de',
            password='testpass123', type='customer',
        )
        self.business_a = CustomUser.objects.create_user(
            username='business_a', email='ba@coderr.de',
            password='testpass123', type='business',
        )
        self.business_b = CustomUser.objects.create_user(
            username='business_b', email='bb@coderr.de',
            password='testpass123', type='business',
        )
        # customer_a -> business_a (customer_a sees this)
        self.order_a = Order.objects.create(
            customer_user=self.customer_a,
            business_user=self.business_a,
            title='Logo Design A',
            revisions=3, delivery_time_in_days=5, price=150,
            features=['Logo'], offer_type='basic',
        )
        # customer_b -> business_b (customer_a should NOT see this)
        self.order_b = Order.objects.create(
            customer_user=self.customer_b,
            business_user=self.business_b,
            title='Logo Design B',
            revisions=3, delivery_time_in_days=5, price=150,
            features=['Logo'], offer_type='basic',
        )
        self.url = reverse('order-list')

    def test_authenticated_customer_sees_only_own_orders(self):
        """A customer only sees orders in which they are listed as customer_user (200)."""
        self.client.force_authenticate(user=self.customer_a)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order_a.pk)

    def test_authenticated_business_sees_only_own_orders(self):
        """A business user only sees orders in which they are listed as business_user (200)."""
        self.client.force_authenticate(user=self.business_a)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order_a.pk)

    def test_user_with_no_orders_gets_empty_list(self):
        """A user without any orders receives an empty list (200)."""
        unrelated_user = CustomUser.objects.create_user(
            username='unrelated', email='u@coderr.de',
            password='testpass123', type='customer',
        )
        self.client.force_authenticate(user=unrelated_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_unauthenticated_user_cannot_list_orders(self):
        """An unauthenticated user receives 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)