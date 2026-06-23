from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferDetailRetrieveTests(APITestCase):
    """Tests for the offer detail endpoint (GET /api/offerdetails/{id}/)."""

    def setUp(self):
        """Creates a business user, a customer user, an offer and an offer detail."""
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
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Grafikdesign-Paket',
            description='Ein umfassendes Grafikdesign-Paket.',
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='basic',
        )
        self.url = reverse('offerdetail-detail', args=[self.offer_detail.pk])

    def test_authenticated_user_can_retrieve_offerdetail(self):
        """An authenticated user can retrieve the detail view of an offer detail (200)."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer_detail.pk)
        self.assertEqual(response.data['title'], 'Basic Design')
        self.assertEqual(response.data['offer_type'], 'basic')

    def test_unauthenticated_user_cannot_retrieve_offerdetail(self):
        """An unauthenticated user receives 401 when retrieving an offer detail."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_offerdetail_returns_404(self):
        """A request for a nonexistent offer detail returns 404."""
        self.client.force_authenticate(user=self.customer_user)
        nonexistent_url = reverse('offerdetail-detail', args=[9999])
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_response_contains_correct_fields(self):
        """The response contains exactly the expected fields per the API documentation."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = {
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        }
        self.assertEqual(set(response.data.keys()), expected_fields)