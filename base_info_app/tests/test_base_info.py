from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoTests(APITestCase):
    """Tests for the base-info endpoint (GET /api/base-info/)."""

    def setUp(self):
        """Creates users, offers and reviews for the aggregation."""
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
        Offer.objects.create(user=self.business_a, title='Offer 1', description='')
        Offer.objects.create(user=self.business_b, title='Offer 2', description='')
        Review.objects.create(business_user=self.business_a, reviewer=self.customer, rating=5, description='')
        Review.objects.create(business_user=self.business_b, reviewer=self.customer, rating=3, description='')
        self.url = reverse('base-info')

    def test_base_info_returns_correct_counts(self):
        """The endpoint returns correct counts for reviews, offers and business profiles (200)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertEqual(response.data['offer_count'], 2)

    def test_base_info_returns_correct_average_rating(self):
        """The average rating is rounded to one decimal place."""
        response = self.client.get(self.url)
        self.assertEqual(response.data['average_rating'], 4.0)  # (5+3)/2

    def test_base_info_is_publicly_accessible(self):
        """The endpoint is reachable without authentication (200)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_average_rating_is_zero_when_no_reviews(self):
        """When there are no reviews, average_rating is 0.0."""
        Review.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.data['average_rating'], 0.0)
        self.assertEqual(response.data['review_count'], 0)