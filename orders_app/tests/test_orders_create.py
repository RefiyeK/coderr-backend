from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderCreateTests(APITestCase):
    """Tests für die Order-Erstellung (POST /api/orders/)."""

    def setUp(self):
        """Erstellt Customer, Business und ein Offer mit drei Details."""
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        self.offer = Offer.objects.create(
            user=self.business,
            title='Grafikdesign-Paket',
            description='Test',
        )
        self.basic_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2, delivery_time_in_days=5, price=100,
            features=['Logo'], offer_type='basic',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Design',
            revisions=5, delivery_time_in_days=7, price=200,
            features=['Logo', 'Visitenkarte'], offer_type='standard',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Design',
            revisions=10, delivery_time_in_days=10, price=500,
            features=['Logo', 'Visitenkarte', 'Briefpapier'], offer_type='premium',
        )
        self.url = reverse('order-list')

    def test_customer_can_create_order_from_offer_detail(self):
        """Ein Customer kann eine Order aus einem OfferDetail erstellen (201)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_created_order_is_snapshot_of_offer_detail(self):
        """Die erstellte Order kopiert alle relevanten Felder vom OfferDetail (Snapshot)."""
        self.client.force_authenticate(user=self.customer)
        self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        order = Order.objects.first()
        self.assertEqual(order.customer_user, self.customer)
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.title, 'Basic Design')
        self.assertEqual(order.revisions, 2)
        self.assertEqual(order.delivery_time_in_days, 5)
        self.assertEqual(order.price, 100)
        self.assertEqual(order.features, ['Logo'])
        self.assertEqual(order.offer_type, 'basic')
        self.assertEqual(order.status, 'in_progress')

    def test_business_user_cannot_create_order(self):
        """Ein Business-User kann keine Order erstellen (403)."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_order(self):
        """Ein nicht authentifizierter User kann keine Order erstellen (401)."""
        response = self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_with_nonexistent_offer_detail_returns_400(self):
        """Eine Anfrage mit einer nicht existierenden offer_detail_id wird mit 400 abgelehnt."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {'offer_detail_id': 9999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_without_offer_detail_id_returns_400(self):
        """Eine Anfrage ohne offer_detail_id wird mit 400 abgelehnt."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)