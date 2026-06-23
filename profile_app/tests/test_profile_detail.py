from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser


class ProfileDetailTests(APITestCase):
    """Tests for the profile detail endpoint (GET/PATCH /api/profile/{pk}/)."""

    def setUp(self):
        """Creates a test user and authenticates them."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@coderr.de',
            password='testpass123',
            type='customer',
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_get_profile(self):
        """An authenticated user can retrieve a profile."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@coderr.de')
        self.assertEqual(response.data['type'], 'customer')

        empty_fields = ['first_name', 'last_name',
                        'location', 'tel', 'description', 'working_hours']
        for field in empty_fields:
            self.assertEqual(response.data[field],
                             "",  f"Field {field} should be empty")

    def test_unauthenticated_user_cannot_get_profile(self):
        """An unauthenticated user receives 401."""
        self.client.force_authenticate(user=None)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_profile_returns_404(self):
        """A nonexistent profile returns 404."""
        url = reverse('profile-detail', kwargs={'pk': 99999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_update_profile(self):
        """The owner can update their profile (200)."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'location': 'Berlin',
            'tel': '0123456789',
            'description': 'Neue Beschreibung',
            'working_hours': '9-17',
            'email': 'new@coderr.de',
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['location'], 'Berlin')
        self.assertEqual(response.data['email'], 'new@coderr.de')

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@coderr.de')

    def test_unauthenticated_user_cannot_update_profile(self):
        """An unauthenticated user cannot update a profile (401)."""
        self.client.force_authenticate(user=None)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {'location': 'Berlin'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_preserves_empty_string_rule(self):
        """In a partial update, fields that are not set remain empty strings."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {'location': 'Berlin'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Berlin')
        empty_fields = ['first_name', 'last_name',
                        'tel', 'description', 'working_hours']
        for field in empty_fields:
            self.assertEqual(response.data[field],
                             "", f"Field {field} should be empty")

    def test_non_owner_cannot_update_profile(self):
        """Another user cannot update the profile (403)."""
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@coderr.de',
            password='pass123',
            type='customer',
        )
        self.client.force_authenticate(user=other_user)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        data = {'location': 'Berlin'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_profile_returns_404(self):
        """A PATCH request for a nonexistent profile returns 404."""
        url = reverse('profile-detail', kwargs={'pk': 99999})
        data = {'location': 'Berlin'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_response_contains_all_expected_fields(self):
        """The GET response contains all expected fields."""
        url = reverse('profile-detail', kwargs={'pk': self.user.id})

        response = self.client.get(url)

        expected_fields = {
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at'
        }
        self.assertSetEqual(set(response.data.keys()), expected_fields)