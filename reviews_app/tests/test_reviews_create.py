from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from reviews_app.models import Review


class ReviewCreateTests(APITestCase):
    """Tests for the review create endpoint (POST /api/reviews/)."""

    def setUp(self):
        """Creates a customer and a business user."""
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        self.url = reverse('review-list')

    def test_customer_can_create_review(self):
        """A customer can create a review for a business user (201)."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'business_user': self.business.pk,
            'rating': 4,
            'description': 'Sehr gut!',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(response.data['reviewer'], self.customer.pk)
        self.assertEqual(response.data['business_user'], self.business.pk)
        self.assertEqual(response.data['rating'], 4)

    def test_business_user_cannot_create_review(self):
        """A business user cannot create a review (403)."""
        self.client.force_authenticate(user=self.business)
        payload = {
            'business_user': self.business.pk,
            'rating': 4,
            'description': 'Test',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 0)

    def test_customer_cannot_create_second_review_for_same_business(self):
        """A customer can only create one review per business user (403)."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'business_user': self.business.pk,
            'rating': 4,
            'description': 'Erste Bewertung',
        }
        first_response = self.client.post(self.url, payload, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        payload['description'] = 'Zweite Bewertung'
        second_response = self.client.post(self.url, payload, format='json')
        self.assertEqual(second_response.status_code,
                         status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_unauthenticated_user_cannot_create_review(self):
        """An unauthenticated user cannot create a review (401)."""
        payload = {
            'business_user': self.business.pk,
            'rating': 4,
            'description': 'Test',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_with_invalid_rating_returns_400(self):
        """A review with a rating outside 1-5 is rejected (400)."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'business_user': self.business.pk,
            'rating': 6,
            'description': 'Ungültig',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviewer_field_is_ignored_in_request_body(self):
        """The reviewer field in the request body is ignored; the reviewer is always the logged-in user."""
        other_customer = CustomUser.objects.create_user(
            username='other_customer', email='oc@coderr.de',
            password='testpass123', type='customer',
        )
        self.client.force_authenticate(user=self.customer)
        payload = {
            'business_user': self.business.pk,
            'reviewer': other_customer.pk,
            'rating': 4,
            'description': 'Test',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.customer.pk)

    def test_create_review_without_description_returns_400(self):
        """A review without description is rejected with 400 (field-level validation runs first)."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'business_user': self.business.pk,
            'rating': 4,
            # description missing on purpose
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_duplicate_review_with_missing_description_returns_400(self):
        """When a request is invalid (missing description), 400 takes priority over the 403 duplicate check."""
        # First, create a valid review
        self.client.force_authenticate(user=self.customer)
        valid_payload = {
            'business_user': self.business.pk,
            'rating': 4,
            'description': 'First review',
        }
        first_response = self.client.post(
            self.url, valid_payload, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        # Now try a second one without description -- must be 400, not 403
        invalid_payload = {
            'business_user': self.business.pk,
            'rating': 5,
            # description missing
        }
        second_response = self.client.post(
            self.url, invalid_payload, format='json')
        self.assertEqual(second_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
