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

        # Zweiter Business-User mit eigenem Offer für Filter-Tests
        self.other_business_user = CustomUser.objects.create_user(
            username='other_business',
            email='other@coderr.de',
            password='testpass123',
            type='business',
        )
        self.other_offer = Offer.objects.create(
            user=self.other_business_user,
            title='Webdesign-Paket',
            description='Modernes Webdesign.',
        )
        OfferDetail.objects.create(
            offer=self.other_offer,
            title='Basic Web',
            revisions=1,
            delivery_time_in_days=14,
            price=300,
            features=['Landing Page'],
            offer_type='basic',
        )
        OfferDetail.objects.create(
            offer=self.other_offer,
            title='Standard Web',
            revisions=3,
            delivery_time_in_days=21,
            price=600,
            features=['Landing Page', '5 Subpages'],
            offer_type='standard',
        )
        OfferDetail.objects.create(
            offer=self.other_offer,
            title='Premium Web',
            revisions=5,
            delivery_time_in_days=30,
            price=1200,
            features=['Landing Page', '10 Subpages', 'SEO'],
            offer_type='premium',
        )

    def test_pagination_returns_paginated_response(self):
        """Die Liste wird paginiert zurückgegeben."""
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 2)

    def test_pagination_respects_page_size(self):
        """Die page_size kann vom Client gesteuert werden."""
        url = reverse('offer-list')
        response = self.client.get(url, {'page_size': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNotNone(response.data['next'])

    def test_search_offers_by_title_or_description(self):
        """Sucht Offers nach Titel oder Description."""
        url = reverse('offer-list')
        response = self.client.get(url, {'search': 'Webdesign'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.other_offer.id)

    def test_filter_offers_by_min_price(self):
        """Filtert Offers nach Mindestpreis (min_price)."""
        url = reverse('offer-list')
        response = self.client.get(url, {'min_price': 600})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.other_offer.id)

    def test_filter_offers_by_max_delivery_time(self):
        """Filtert Offers nach maximaler Lieferzeit (max_delivery_time)."""
        url = reverse('offer-list')
        response = self.client.get(url, {'max_delivery_time': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.offer.id)

    def test_filter_offers_by_creator_id(self):
        """Filtert Offers nach creator_id (User-ID)."""
        url = reverse('offer-list')
        response = self.client.get(url, {'creator_id': self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.business_user.id)

    def test_offer_list_response_structure(self):
        """Die Response enthält die erwarteten Felder mit korrekten Werten."""
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        offer = next(o for o in response.data['results'] if o['id'] == self.offer.id)
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

    def test_order_offers_by_min_price_ascending(self):
        """Sortiert Offers aufsteigend nach min_price."""
        url = reverse('offer-list')
        response = self.client.get(url, {'ordering': 'min_price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.offer.id)
        self.assertEqual(response.data['results'][1]['id'], self.other_offer.id)

        # Beweis: Auch absteigend funktioniert (kein zufälliger Default-Treffer)
        response_desc = self.client.get(url, {'ordering': '-min_price'})
        self.assertEqual(response_desc.data['results'][0]['id'], self.other_offer.id)
        self.assertEqual(response_desc.data['results'][1]['id'], self.offer.id)

    def test_order_offers_by_updated_at_descending(self):
        """Sortiert Offers absteigend nach updated_at (neueste zuerst)."""
        url = reverse('offer-list')
        response = self.client.get(url, {'ordering': '-updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.other_offer.id)
        self.assertEqual(response.data['results'][1]['id'], self.offer.id)
