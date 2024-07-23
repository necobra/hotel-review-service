from django.test import TestCase
from hotel_review_service.models import (
    Hotel,
    HotelClass,
    User
)
from hotel_review_service.forms import (
    HotelForm,
    HotelSearchForm,
    ReviewForm,
    ReviewSearchForm,
    UserSearchForm
)


class FormsTestCase(TestCase):
    fixtures = ["initial_data.json"]

    def test_hotel_form_valid_data(self):
        form_data = {
            "name": "Test Hotel",
            "hotel_class": HotelClass.objects.first().id,
            "country": "Ukraine",
            "city": "Kyiv",
            "address": "1234 Khreshchatyk St",
        }
        form = HotelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_hotel_form_initialization_with_instance(self):
        hotel = Hotel.objects.first()
        form = HotelForm(instance=hotel)
        self.assertEqual(form.initial.get("country"), hotel.placement.country)
        self.assertEqual(form.initial.get("city"), hotel.placement.city)
        self.assertEqual(form.initial.get("address"), hotel.placement.address)

    def test_hotel_form_invalid_data(self):
        form_data = {
            "name": "",
            "hotel_class": None,
            "country": "",
            "city": "",
            "address": "",
        }
        form = HotelForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("hotel_class", form.errors)
        self.assertIn("country", form.errors)
        self.assertIn("city", form.errors)
        self.assertIn("address", form.errors)

    def test_hotel_search_form_valid_data(self):
        form_data = {"search": "Kyiv"}
        form = HotelSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_valid_data(self):
        form_data = {
            "caption": "Test Review",
            "comment": "This is a test comment.",
            "hotel_rating": 8,
            "hotel": Hotel.objects.first().id,
            "author": User.objects.first().id,
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_data(self):
        form_data = {
            "caption": "",
            "comment": "",
            "hotel_rating": 15,
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("caption", form.errors)
        self.assertIn("comment", form.errors)
        self.assertIn("hotel_rating", form.errors)

    def test_review_search_form_valid_data(self):
        form_data = {"search": "Good experience"}
        form = ReviewSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_search_form_valid_data(self):
        form_data = {"search": "admin"}
        form = UserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
