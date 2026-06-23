from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import CustomUser


class LoginTests(APITestCase):
    """Tests for the user login endpoint."""

    def setUp(self):
        """Creates a test user before each test."""
        self.url = reverse('login')
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@coderr.de',
            password='testpass123',
            type='customer',
        )

    def test_login_with_valid_credentials_returns_200(self):
        """Login with valid credentials returns 200 and a token."""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_with_wrong_password_returns_400(self):
        """Login with a wrong password returns 400."""
        data = {
            'username': 'testuser',
            'password': 'wrongpass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_nonexistent_user_returns_400(self):
        """Login with a nonexistent user returns 400."""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)