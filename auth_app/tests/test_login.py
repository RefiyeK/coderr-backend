from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser


class LoginTests(APITestCase):
    """Tests für den Login von Benutzern."""

    def setUp(self):
        """Erstellt einen Testbenutzer vor jedem Test."""
        self.url = reverse('login')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@coderr.de',
            password='testpass123',
            type='customer',
        )

    def test_login_with_valid_credentials_returns_200(self):
        """Login mit gültigen Daten gibt 200 und Token zurück."""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_with_wrong_password_returns_400(self):
        """Login mit falschem Passwort gibt 400 zurück."""
        data = {
            'username': 'testuser',
            'password': 'wrongpass123',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_nonexistent_user_returns_400(self):
        """Login mit nicht existierendem Benutzer gibt 400 zurück."""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
