from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from reviews_app.models import Review


class ReviewUpdateTests(APITestCase):
    """Tests for the review update endpoint (PATCH /api/reviews/<id>/)."""

    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.other_customer = CustomUser.objects.create_user(
            username='other_customer', email='oc@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description='Original',
        )
        self.url = reverse('review-detail', args=[self.review.pk])

    def test_reviewer_can_update_own_review(self):
        """The creator of the review can update it (200)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(self.url, {'rating': 5, 'description': 'Updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, 'Updated')

    def test_other_user_cannot_update_review(self):
        """Another user cannot update the review (403)."""
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.patch(self.url, {'rating': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)

    def test_unauthenticated_user_cannot_update_review(self):
        """An unauthenticated user cannot update the review (401)."""
        response = self.client.patch(self.url, {'rating': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_user_field_cannot_be_changed(self):
        """The business_user field cannot be changed via PATCH (read-only)."""
        other_business = CustomUser.objects.create_user(
            username='other_business', email='ob@coderr.de',
            password='testpass123', type='business',
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(self.url, {'business_user': other_business.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.business_user, self.business)

    def test_update_nonexistent_review_returns_404(self):
        """A PATCH request for a nonexistent review returns 404."""
        self.client.force_authenticate(user=self.customer)
        nonexistent_url = reverse('review-detail', args=[9999])
        response = self.client.patch(nonexistent_url, {'rating': 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReviewDestroyTests(APITestCase):
    """Tests for deleting a review (DELETE /api/reviews/<id>/)."""

    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='customer_user', email='c@coderr.de',
            password='testpass123', type='customer',
        )
        self.other_customer = CustomUser.objects.create_user(
            username='other_customer', email='oc@coderr.de',
            password='testpass123', type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business_user', email='b@coderr.de',
            password='testpass123', type='business',
        )
        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description='Test',
        )
        self.url = reverse('review-detail', args=[self.review.pk])

    def test_reviewer_can_delete_own_review(self):
        """The creator of the review can delete it (204)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_other_user_cannot_delete_review(self):
        """Another user cannot delete the review (403)."""
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_unauthenticated_user_cannot_delete_review(self):
        """An unauthenticated user cannot delete the review (401)."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 1)

    def test_delete_nonexistent_review_returns_404(self):
        """A DELETE request for a nonexistent review returns 404."""
        self.client.force_authenticate(user=self.customer)
        nonexistent_url = reverse('review-detail', args=[9999])
        response = self.client.delete(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)