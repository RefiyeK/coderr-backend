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


class OfferDetailDestroyTests(APITestCase):
    """Tests für die Löschung eines Offers (DELETE /api/offers/{id}/)."""

    def setUp(self):
        """Erstellt zwei Business-User, einen Customer-User und ein Offer mit drei Details."""
        self.owner = CustomUser.objects.create_user(
            username='offer_owner',
            email='owner@coderr.de',
            password='testpass123',
            type='business',
        )
        self.other_business = CustomUser.objects.create_user(
            username='other_business',
            email='other_biz@coderr.de',
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
            user=self.owner,
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

    def test_owner_can_delete_offer(self):
        """Der Eigentümer eines Offers kann es löschen (204)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_non_owner_business_user_cannot_delete_offer(self):
        """Ein anderer Business-User kann ein fremdes Offer nicht löschen (403)."""
        self.client.force_authenticate(user=self.other_business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 1)

    def test_customer_user_cannot_delete_offer(self):
        """Ein Customer-User kann ein Offer nicht löschen (403)."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 1)

    def test_unauthenticated_user_cannot_delete_offer(self):
        """Ein nicht authentifizierter User kann kein Offer löschen (401)."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Offer.objects.count(), 1)

    def test_delete_nonexistent_offer_returns_404(self):
        """Eine DELETE-Anfrage an ein nicht existierendes Offer gibt 404 zurück."""
        self.client.force_authenticate(user=self.owner)
        nonexistent_url = reverse('offer-detail', args=[9999])
        response = self.client.delete(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Offer.objects.count(), 1)


class OfferDetailUpdateTests(APITestCase):
    """Tests für die Aktualisierung eines Offers (PATCH /api/offers/{id}/)."""

    def setUp(self):
        """Erstellt zwei Business-User, einen Customer-User und ein Offer mit drei Details."""
        self.owner = CustomUser.objects.create_user(
            username='offer_owner',
            email='owner@coderr.de',
            password='testpass123',
            type='business',
        )
        self.other_business = CustomUser.objects.create_user(
            username='other_business',
            email='other_biz@coderr.de',
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
            user=self.owner,
            title='Grafikdesign-Paket',
            description='Ein umfassendes Grafikdesign-Paket.',
        )
        self.basic_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo Design'],
            offer_type='basic',
        )
        self.standard_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Design',
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='standard',
        )
        self.premium_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Design',
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=['Logo Design', 'Visitenkarte', 'Briefpapier'],
            offer_type='premium',
        )
        self.url = reverse('offer-detail', args=[self.offer.pk])

    def test_owner_can_update_offer_title_only(self):
        """Der Eigentümer kann nur den Titel aktualisieren, ohne Details mitzusenden (200)."""
        self.client.force_authenticate(user=self.owner)
        payload = {'title': 'Updated Grafikdesign-Paket'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Grafikdesign-Paket')
        # Details bleiben unverändert
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.details.count(), 3)
        self.basic_detail.refresh_from_db()
        self.assertEqual(self.basic_detail.price, 100)

    def test_owner_can_update_single_detail_by_offer_type(self):
        """Der Eigentümer kann ein einzelnes Detail aktualisieren, andere bleiben unverändert (200)."""
        self.client.force_authenticate(user=self.owner)
        payload = {
            'details': [
                {'offer_type': 'basic', 'price': 999}
            ]
        }
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Basic-Detail wurde aktualisiert, ID bleibt gleich
        self.basic_detail.refresh_from_db()
        self.assertEqual(self.basic_detail.price, 999)
        self.assertEqual(self.basic_detail.revisions, 2)  # unverändert
        # Standard- und Premium-Detail bleiben unverändert
        self.standard_detail.refresh_from_db()
        self.premium_detail.refresh_from_db()
        self.assertEqual(self.standard_detail.price, 200)
        self.assertEqual(self.premium_detail.price, 500)
        # Es existieren weiterhin genau 3 Details
        self.assertEqual(self.offer.details.count(), 3)

    def test_unauthenticated_user_cannot_update_offer(self):
        """Ein nicht authentifizierter User kann kein Offer aktualisieren (401)."""
        payload = {'title': 'Hacked Title'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Grafikdesign-Paket')

    def test_non_owner_business_user_cannot_update_offer(self):
        """Ein anderer Business-User kann ein fremdes Offer nicht aktualisieren (403)."""
        self.client.force_authenticate(user=self.other_business)
        payload = {'title': 'Hacked Title'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Grafikdesign-Paket')

    def test_update_with_too_many_details_returns_400(self):
        """Mehr als 3 Details im PATCH werden mit 400 abgelehnt."""
        self.client.force_authenticate(user=self.owner)
        payload = {
            'details': [
                {'offer_type': 'basic', 'price': 100},
                {'offer_type': 'standard', 'price': 200},
                {'offer_type': 'premium', 'price': 500},
                {'offer_type': 'basic', 'price': 999},
            ]
        }
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_duplicate_offer_type_returns_400(self):
        """Doppelter offer_type im PATCH wird mit 400 abgelehnt."""
        self.client.force_authenticate(user=self.owner)
        payload = {
            'details': [
                {'offer_type': 'basic', 'price': 100},
                {'offer_type': 'basic', 'price': 200},
                {'offer_type': 'premium', 'price': 500},
            ]
        }
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
