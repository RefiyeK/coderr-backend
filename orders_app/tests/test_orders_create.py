from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderCreateTests(APITestCase):
    """Tests for the order create endpoint (POST /api/orders/)."""

    def setUp(self):
        """Creates a customer, a business user, and an offer with three details."""
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
        """A customer can create an order from an offer detail (201)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_created_order_is_snapshot_of_offer_detail(self):
        """The created order copies all relevant fields from the offer detail (snapshot)."""
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
        """A business user cannot create an order (403)."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_order(self):
        """An unauthenticated user cannot create an order (401)."""
        response = self.client.post(self.url, {'offer_detail_id': self.basic_detail.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_with_nonexistent_offer_detail_returns_404(self):
        """A request with a nonexistent offer_detail_id is rejected with 404."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {'offer_detail_id': 9999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_without_offer_detail_id_returns_400(self):
        """A request without offer_detail_id is rejected with 400."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)