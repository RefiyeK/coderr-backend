from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import CustomUser


class BusinessProfileListTests(APITestCase):
    """Tests für den Business-Profile-List Endpoint (GET /api/profiles/business/)."""

    def setUp(self):
        """Erstellt einen Business-User und authentifiziert ihn."""
        self.user = CustomUser.objects.create_user(
            username='business_user',
            email='biz@coderr.de',
            password='testpass123',
            type='business',
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_list_business_profiles(self):
        """Ein authentifizierter Benutzer kann die Liste der Business-Profile abrufen."""
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


    def test_business_profile_response_uses_empty_strings(self):
        """Leere Felder werden als leere Strings, nicht als null zurückgegeben."""
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data[0]
        empty_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in empty_fields:
            self.assertEqual(profile[field], "", f"Feld {field} sollte leer sein")

    def test_unauthenticated_user_cannot_list_business_profiles(self):
        """Ein nicht authentifizierter Benutzer erhält 401."""
        self.client.force_authenticate(user=None)
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class CustomerProfileListTests(APITestCase):
    """Tests für den Customer-Profile-List Endpoint (GET /api/profiles/customer/)."""

    def setUp(self):
        """Erstellt einen Customer-User und authentifiziert ihn."""
        self.user = CustomUser.objects.create_user(
            username='customer_user',
            email='cust@coderr.de',
            password='testpass123',
            type='customer',
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_list_customer_profiles(self):
        """Ein authentifizierter Benutzer kann die Liste der Customer-Profile abrufen."""
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_customer_profile_response_uses_empty_strings(self):
        """Leere Felder werden als leere Strings zurückgegeben."""
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data[0]
        empty_fields = ['first_name', 'last_name']
        for field in empty_fields:
            self.assertEqual(profile[field], "", f"Feld {field} sollte leer sein")
        self.assertIn('uploaded_at', profile)

    def test_unauthenticated_user_cannot_list_customer_profiles(self):
        """Ein nicht authentifizierter Benutzer erhält 401."""
        self.client.force_authenticate(user=None)
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_business_profiles(self):
    #     """Testet, ob der Endpoint eine Liste von Business-Profilen zurückgibt."""
    #     url = reverse('business-profile-list')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIsInstance(response.data, list)