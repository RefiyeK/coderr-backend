from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferListTests(APITestCase):
    """Tests für den Offer-List Endpoint (GET /api/offers/)."""

    def setUp(self):
        """Erstellt einen Business-User, einen Offer und drei OfferDetails."""
        self.business_user = CustomUser.objects.create_user(
            username='business_user',
            email='biz@coderr.de',
            password='testpass123',
            type='business',
        )
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Grafikdesign-Paket',
            description='Ein umfassendes Grafikdesign-Paket.',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='basic',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Design',
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=['Logo Design', 'Visitenkarte', 'Briefpapier'],
            offer_type='standard',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Design',
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=['Logo Design', 'Visitenkarte', 'Briefpapier', 'Flyer'],
            offer_type='premium',
        )

    def test_offer_list_response_structure(self):
        """Die Response enthält die erwarteten Felder mit korrekten Werten."""
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        offer = response.data[0]
        self.assertEqual(offer['title'], 'Grafikdesign-Paket')
        self.assertEqual(offer['user'], self.business_user.id)
        self.assertEqual(offer['min_price'], 100)
        self.assertEqual(offer['min_delivery_time'], 5)
        self.assertEqual(len(offer['details']), 3)
        self.assertEqual(offer['user_details']['username'], 'business_user')
        

    def test_unauthenticated_user_can_list_offers(self):
        """Auch nicht-authentifizierte Benutzer können Offers abrufen."""
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    