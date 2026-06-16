from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferDetailRetrieveTests(APITestCase):
    """Tests für den Offer-Detail Endpoint (GET /api/offers/{id}/)."""

    def setUp(self):
        """Erstellt einen Business-User, einen Customer-User und ein Offer mit drei Details."""
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
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo Design'],
            offer_type='basic',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Design',
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='standard',
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Design',
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=['Logo Design', 'Visitenkarte', 'Briefpapier'],
            offer_type='premium',
        )
        self.url = reverse('offer-detail', args=[self.offer.pk])

    def test_authenticated_user_can_retrieve_offer(self):
        """Ein authentifizierter User kann die Detail-Ansicht eines Offers abrufen (200)."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.pk)
        self.assertEqual(response.data['title'], 'Grafikdesign-Paket')

    def test_unauthenticated_user_cannot_retrieve_offer(self):
        """Ein nicht authentifizierter User erhält 401 beim Abrufen eines Offers."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_offer_returns_404(self):
        """Eine Anfrage nach einem nicht existierenden Offer gibt 404 zurück."""
        self.client.force_authenticate(user=self.customer_user)
        nonexistent_url = reverse('offer-detail', args=[9999])
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_response_excludes_user_details_field(self):
        """Die Detail-Response enthält kein user_details-Feld (im Unterschied zur Liste)."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('user_details', response.data)
        # Stelle gleichzeitig sicher, dass die erwarteten Felder vorhanden sind
        expected_fields = {
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time',
        }
        self.assertEqual(set(response.data.keys()), expected_fields)