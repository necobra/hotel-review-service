from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import generic

from .models import Hotel, Review


def index(request):
    """View function for the home page of the site."""

    num_users = get_user_model().objects.count()
    num_hotels = Hotel.objects.count()
    num_reviews = Review.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_users": num_users,
        "num_hotels": num_hotels,
        "num_reviews": num_reviews,
        "num_visits": num_visits + 1,
    }

    return render(request, "hotel_review_service/index.html", context=context)


class HotelListView(generic.ListView):
    model = Hotel
    queryset = Hotel.objects.select_related("placement", "hotel_class").prefetch_related("reviews")
    paginate_by = 5


class ReviewListView(generic.ListView):
    model = Review
    queryset = Review.objects.select_related("user", "hotel")
    paginate_by = 5


class UserListView(generic.ListView):
    model = get_user_model()
    paginate_by = 5
