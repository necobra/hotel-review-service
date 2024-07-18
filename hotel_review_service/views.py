from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from .models import Hotel, Review


@login_required
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


class HotelListView(LoginRequiredMixin, generic.ListView):
    model = Hotel
    queryset = Hotel.objects.select_related("placement", "hotel_class").prefetch_related("reviews")
    paginate_by = 5


class HotelDetailView(LoginRequiredMixin, generic.DetailView):
    model = Hotel
    queryset = Hotel.objects.select_related("placement", "hotel_class").prefetch_related("reviews")


class ReviewListView(LoginRequiredMixin, generic.ListView):
    model = Review
    queryset = Review.objects.select_related("user", "hotel")
    paginate_by = 5


class ReviewDetailView(LoginRequiredMixin, generic.DetailView):
    model = Review
    queryset = Review.objects.select_related("user", "hotel")


class UserListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
