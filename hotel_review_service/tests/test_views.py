from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.test import TestCase
from django.urls import reverse

from hotel_review_service.models import Hotel, Review


class PrivateHotelListTest(TestCase):
    HOTEL_LIST_URL = reverse("hotel_review_service:hotel-list")
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)

    def test_retrieve_hotels(self):
        response = self.client.get(self.HOTEL_LIST_URL)
        self.assertEqual(response.status_code, 200)
        hotels = Hotel.objects.all()[:5]
        self.assertEqual(
            list(response.context["hotel_list"]),
            list(hotels)
        )
        self.assertTemplateUsed(response, "hotel_review_service/hotel_list.html")

    def test_hotel_search(self):
        criteria = "Kyiv"
        response = self.client.get(self.HOTEL_LIST_URL + f"?search={criteria}")
        self.assertEqual(response.status_code, 200)
        manufacturers = Hotel.objects.filter(name__icontains=criteria)
        self.assertEqual(
            list(response.context["hotel_list"]),
            list(manufacturers)
        )


class PrivateUserListTest(TestCase):
    USER_LIST_URL = reverse("hotel_review_service:user-list")
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)

    def test_retrieve_users(self):
        response = self.client.get(self.USER_LIST_URL)
        self.assertEqual(response.status_code, 200)
        users = get_user_model().objects.all()[:5]
        self.assertEqual(
            list(response.context["user_list"]),
            list(users)
        )
        self.assertTemplateUsed(response, "hotel_review_service/user_list.html")

    def test_user_search(self):
        criteria = "testuser"
        response = self.client.get(self.USER_LIST_URL + f"?search={criteria}")
        self.assertEqual(response.status_code, 200)
        users = get_user_model().objects.filter(username__icontains=criteria)
        self.assertEqual(
            list(response.context["user_list"]),
            list(users)
        )

class PrivateReviewListTest(TestCase):
    REVIEW_LIST_URL = reverse("hotel_review_service:review-list")
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)

    def test_retrieve_reviews(self):
        response = self.client.get(self.REVIEW_LIST_URL)
        self.assertEqual(response.status_code, 200)
        reviews = Review.objects.all()[:5]
        self.assertEqual(
            list(response.context["review_list"]),
            list(reviews)
        )
        self.assertTemplateUsed(response, "hotel_review_service/review_list.html")

    def test_review_search(self):
        criteria = "test"
        response = self.client.get(self.REVIEW_LIST_URL + f"?search={criteria}")
        self.assertEqual(response.status_code, 200)
        reviews = Review.objects.filter(caption__icontains=criteria)
        self.assertEqual(
            list(response.context["review_list"]),
            list(reviews)
        )


class PrivateUserDetailTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)
        self.user_detail_url = reverse("hotel_review_service:user-detail", args=[self.user.id])

    def test_user_detail_view(self):
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotel_review_service/user_detail.html")
        self.assertEqual(response.context["user"].username, self.user.username)
        self.assertEqual(response.context["user"].id, self.user.id)
        reviews_amount = Review.objects.filter(author=self.user).count()
        self.assertEqual(response.context["user"].reviews_amount, reviews_amount)


class PrivateHotelDetailTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)
        self.hotel = Hotel.objects.get(id=1)
        self.hotel_detail_url = reverse("hotel_review_service:hotel-detail", args=[self.hotel.id])

    def test_hotel_detail_view(self):
        response = self.client.get(self.hotel_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotel_review_service/hotel_detail.html")
        self.assertEqual(response.context["hotel"].name, self.hotel.name)
        self.assertEqual(response.context["hotel"].id, self.hotel.id)
        self.assertEqual(response.context["hotel"].placement.country, self.hotel.placement.country)
        self.assertEqual(response.context["hotel"].placement.city, self.hotel.placement.city)
        self.assertEqual(response.context["hotel"].placement.address, self.hotel.placement.address)

        average_rating = Review.objects.filter(hotel=self.hotel).aggregate(Avg("hotel_rating"))["hotel_rating__avg"]
        self.assertEqual(response.context["hotel"].average_rating, average_rating)

        hotel_reviews = list(Review.objects.filter(hotel=self.hotel))
        self.assertEqual(list(response.context["hotel_reviews"]), hotel_reviews)


class PrivateIndexTest(TestCase):
    INDEX_URL = reverse("hotel_review_service:index")
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)

    def test_index_view(self):
        response = self.client.get(self.INDEX_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotel_review_service/index.html")

        num_users = get_user_model().objects.count()
        num_hotels = Hotel.objects.count()
        num_reviews = Review.objects.count()

        self.assertEqual(response.context["num_users"], num_users)
        self.assertEqual(response.context["num_hotels"], num_hotels)
        self.assertEqual(response.context["num_reviews"], num_reviews)
