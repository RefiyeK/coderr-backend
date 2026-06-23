from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferCreateTests(APITestCase):
    """Tests for the offer create endpoint (POST /api/offers/)."""

    def setUp(self):
        """Creates a business user, a customer user, and a valid request body."""
        self.business_user = CustomUser.objects.create_user(
            username='business_user',
            email='biz@coderr.de',
            password='testpass123',
            type='business',
        )
        self.customer_user = CustomUser.objects.create_user(
            username='customer_user',
            email='cust@coderr.de',
            password='testpass123',
            type='customer',
        )
        self.url = reverse('offer-list')
        self.valid_payload = {
            'title': 'Grafikdesign-Paket',
            'description': 'Ein umfassendes Grafikdesign-Paket.',
            'details': [
                {
                    'title': 'Basic Design',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100,
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard Design',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200,
                    'features': ['Logo Design', 'Visitenkarte', 'Briefpapier'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium Design',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500,
                    'features': ['Logo Design', 'Visitenkarte', 'Briefpapier', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

    def test_business_user_can_create_offer(self):
        """An authenticated business user can create a valid offer (201)."""
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)
        self.assertEqual(Offer.objects.first().user, self.business_user)

    def test_unauthenticated_user_cannot_create_offer(self):
        """An unauthenticated user receives 401 when creating an offer."""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Offer.objects.count(), 0)

    def test_customer_user_cannot_create_offer(self):
        """An authenticated customer user receives 403 when creating an offer."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 0)

    def test_offer_must_have_exactly_three_details(self):
        """An offer with fewer than 3 details is rejected with 400."""
        self.client.force_authenticate(user=self.business_user)
        payload = self.valid_payload.copy()
        payload['details'] = self.valid_payload['details'][:2]  # only 2 details
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)

    def test_invalid_price_type_returns_400(self):
        """A detail with an invalid price type (string instead of number) is rejected with 400."""
        self.client.force_authenticate(user=self.business_user)
        payload = self.valid_payload.copy()
        payload['details'] = [dict(d) for d in self.valid_payload['details']]
        payload['details'][0]['price'] = 'abc'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)