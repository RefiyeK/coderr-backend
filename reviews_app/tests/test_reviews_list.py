from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from reviews_app.models import Review


class ReviewListTests(APITestCase):
    """Tests for the review list endpoint (GET /api/reviews/)."""

    def setUp(self):
        """Creates a user and two reviews for two different business users."""
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.business_a = CustomUser.objects.create_user(
            username='business_a', email='ba@coderr.de',
            password='testpass123', type='business',
        )
        self.business_b = CustomUser.objects.create_user(
            username='business_b', email='bb@coderr.de',
            password='testpass123', type='business',
        )
        self.review_a = Review.objects.create(
            business_user=self.business_a,
            reviewer=self.customer,
            rating=5,
            description='Sehr gut',
        )
        self.review_b = Review.objects.create(
            business_user=self.business_b,
            reviewer=self.customer,
            rating=3,
            description='Mittel',
        )
        self.url = reverse('review-list')

    def test_authenticated_user_can_list_reviews(self):
        """An authenticated user can retrieve the review list (200)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_user_cannot_list_reviews(self):
        """An unauthenticated user receives 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_can_be_filtered_by_business_user_id(self):
        """The business_user_id filter returns only reviews for that business user."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url, {'business_user_id': self.business_a.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['business_user'], self.business_a.pk)