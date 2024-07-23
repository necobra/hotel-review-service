from django.contrib.auth import get_user_model
from django.test import TestCase

from hotel_review_service.models import Review
from hotel_review_service.utils import get_reviews_with_calculated_fields


class ReviewTests(TestCase):
    fixtures = ["initial_data.json"]

    def test_review_review_rating_without_calculated_fields(self):
        review = Review.objects.get(id=1)
        self.assertEqual(review.review_rating,
                         0,
                         "the review should have review rating zero")

    def test_review_review_rating_with_calculated_fields(self):
        review = get_reviews_with_calculated_fields(Review.objects).get(id=1)
        self.assertEqual(review.review_rating, 4)
        self.assertEqual(review.like_amount, 4)
        self.assertEqual(review.dislike_amount, 0)

class UserTest(TestCase):
    fixtures = ["initial_data.json"]

    def test_user_without_likes(self):
        user = get_user_model().objects.get(id=7)
        self.assertEqual(user.liked, [])

    def test_user_likes(self):
        user = get_user_model().objects.get(id=5)
        review_ids_should_be_liked = [1, 3]
        for review_id in review_ids_should_be_liked:
            self.assertIn(Review.objects.get(id=review_id), user.liked)
