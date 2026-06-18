from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from orders_app.models import Order


class OrderUpdateTests(APITestCase):
    """Tests für die Status-Aktualisierung einer Order (PATCH /api/orders/<id>/)."""

    def setUp(self):
        """Erstellt Customer, zwei Business-User und eine Order."""
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        self.other_business = CustomUser.objects.create_user(
            username='other_business', email='ob@coderr.de',
            password='testpass123', type='business',
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Logo Design',
            revisions=3, delivery_time_in_days=5, price=150,
            features=['Logo'], offer_type='basic',
        )
        self.url = reverse('order-detail', args=[self.order.pk])

    def test_business_owner_can_update_status(self):
        """Der business_user der Order kann den Status aktualisieren (200)."""
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_customer_cannot_update_status(self):
        """Der customer_user kann den Status nicht aktualisieren (403)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_other_business_user_cannot_update_status(self):
        """Ein fremder Business-User kann den Status nicht aktualisieren (403)."""
        self.client.force_authenticate(user=self.other_business)
        response = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_status(self):
        """Ein nicht authentifizierter User kann den Status nicht aktualisieren (401)."""
        response = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_status_value_returns_400(self):
        """Ein ungültiger Status-Wert wird mit 400 abgelehnt."""
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(self.url, {'status': 'invalid_status'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_order_returns_404(self):
        """Eine PATCH-Anfrage an eine nicht existierende Order gibt 404 zurück."""
        self.client.force_authenticate(user=self.business)
        nonexistent_url = reverse('order-detail', args=[9999])
        response = self.client.patch(nonexistent_url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDestroyTests(APITestCase):
    """Tests für das Löschen einer Order (DELETE /api/orders/<id>/)."""

    def setUp(self):
        """Erstellt Customer, Business, Staff und eine Order."""
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        self.staff = CustomUser.objects.create_user(
            username='staff_user', email='s@coderr.de',
            password='testpass123', type='business', is_staff=True,
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Logo Design',
            revisions=3, delivery_time_in_days=5, price=150,
            features=['Logo'], offer_type='basic',
        )
        self.url = reverse('order-detail', args=[self.order.pk])

    def test_staff_user_can_delete_order(self):
        """Ein Staff-User kann eine Order löschen (204)."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_business_user_cannot_delete_order(self):
        """Ein normaler Business-User kann keine Order löschen (403)."""
        self.client.force_authenticate(user=self.business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 1)

    def test_customer_cannot_delete_order(self):
        """Ein Customer kann keine Order löschen (403)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 1)

    def test_unauthenticated_user_cannot_delete_order(self):
        """Ein nicht authentifizierter User kann keine Order löschen (401)."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 1)