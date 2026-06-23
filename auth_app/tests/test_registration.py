from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    """Tests for the user registration endpoint."""

    def test_register_valid_customer_returns_201(self):
        """A valid customer registration returns 201 and a token."""
        url = reverse('registration')
        data = {
            'username': 'newcustomer',
            'email': 'new@coderr.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'newcustomer')

    def test_register_with_password_mismatch_returns_400(self):
        """If the passwords do not match, 400 is returned."""
        url = reverse('registration')
        data = {
            'username': 'newcustomer',
            'email': 'new@coderr.de',
            'password': 'testpass123',
            'repeated_password': 'differentpass123',
            'type': 'customer',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_with_duplicate_username_returns_400(self):
        """If the username already exists, 400 is returned."""
        url = reverse('registration')
        data = {
            'username': 'testcustomer',
            'email': 'existing@coderr.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }
        response = self.client.post(url, data, format='json')
        data['email'] = 'another@coderr.de'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_with_invalid_type_returns_400(self):
        """If the type is invalid, 400 is returned."""
        url = reverse('registration')
        data = {
            'username': 'someuser',
            'email': 'some@coderr.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'admin',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)