from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser


class BusinessProfileListTests(APITestCase):
    """Tests for the business profile list endpoint (GET /api/profiles/business/)."""

    def setUp(self):
        """Creates a business user and authenticates them."""
        self.user = CustomUser.objects.create_user(
            username='business_user',
            email='biz@coderr.de',
            password='testpass123',
            type='business',
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_list_business_profiles(self):
        """An authenticated user can retrieve the list of business profiles."""
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_business_profile_response_uses_empty_strings(self):
        """Empty fields are returned as empty strings, not as null."""
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data[0]
        empty_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in empty_fields:
            self.assertEqual(profile[field], "", f"Field {field} should be empty")

    def test_unauthenticated_user_cannot_list_business_profiles(self):
        """An unauthenticated user receives 401."""
        self.client.force_authenticate(user=None)
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerProfileListTests(APITestCase):
    """Tests for the customer profile list endpoint (GET /api/profiles/customer/)."""

    def setUp(self):
        """Creates a customer user and authenticates them."""
        self.user = CustomUser.objects.create_user(
            username='customer_user',
            email='cust@coderr.de',
            password='testpass123',
            type='customer',
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_list_customer_profiles(self):
        """An authenticated user can retrieve the list of customer profiles."""
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_customer_profile_response_uses_empty_strings(self):
        """Empty fields are returned as empty strings."""
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data[0]
        empty_fields = ['first_name', 'last_name']
        for field in empty_fields:
            self.assertEqual(profile[field], "", f"Field {field} should be empty")
        self.assertIn('uploaded_at', profile)

    def test_unauthenticated_user_cannot_list_customer_profiles(self):
        """An unauthenticated user receives 401."""
        self.client.force_authenticate(user=None)
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)