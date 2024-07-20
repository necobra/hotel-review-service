from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import HotelSearchForm
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
    paginate_by = 5

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        hotel_name = self.request.GET.get("search", "")
        context["search_form"] = HotelSearchForm(
            initial={"hotel_name": hotel_name}
        )
        return context

    def get_queryset(self):
        queryset = (
            Hotel.objects.select_related("placement", "hotel_class")
            .prefetch_related("reviews")
            .annotate(average_rating=Avg("reviews__hotel_rating"))
        )
        form = HotelSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["search"])
        return queryset


class HotelDetailView(LoginRequiredMixin, generic.DetailView):
    model = Hotel
    queryset = (
        Hotel.objects.select_related("placement", "hotel_class")
        .prefetch_related("reviews")
        .annotate(average_rating=Avg("reviews__hotel_rating"))
    )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hotel_reviews"] = (
            context["hotel"].reviews.select_related("hotel", "author")
            .prefetch_related("reacted_by").annotate(
                like_amount=Count("userreviewreaction",
                                  filter=Q(userreviewreaction__reaction="L")),
                dislike_amount=Count("userreviewreaction",
                                     filter=Q(userreviewreaction__reaction="D"))
            )
        )
        return context


class HotelCreateView(LoginRequiredMixin, generic.CreateView):
    model = Hotel
    fields = "__all__"
    success_url = reverse_lazy("hotel_review_service:hotel-list")


class HotelUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Hotel
    fields = "__all__"
    success_url = reverse_lazy("hotel_review_service:hotel-list")


class HotelDeleteView(LoginRequiredMixin, generic.DetailView):
    model = Hotel
    success_url = reverse_lazy("hotel_review_service:hotel-list")


class ReviewListView(LoginRequiredMixin, generic.ListView):
    model = Review
    queryset = (
        Review.objects.select_related("hotel", "author")
        .prefetch_related("reacted_by")
        .annotate(
            like_amount=Count("userreviewreaction",
                              filter=Q(userreviewreaction__reaction="L")),
            dislike_amount=Count("userreviewreaction",
                                 filter=Q(userreviewreaction__reaction="D"))
        )
    )
    paginate_by = 5


class ReviewDetailView(LoginRequiredMixin, generic.DetailView):
    model = Review
    queryset = Review.objects.select_related("user", "hotel")


class ReviewCreateView(LoginRequiredMixin, generic.CreateView):
    model = Review
    fields = "__all__"
    success_url = reverse_lazy("hotel_review_service:review-list")


class ReviewUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Review
    fields = "__all__"
    success_url = reverse_lazy("hotel_review_service:review-list")


class ReviewDeleteView(LoginRequiredMixin, generic.DetailView):
    model = Review
    success_url = reverse_lazy("hotel_review_service:review-list")


def review_rate(request, pk: int):
    review = get_object_or_404(Review, id=pk)
    if request.method == "POST":
        if review.author == request.user:
            HttpResponse(status=100)
            # todo print to user you cannot vote for your review
        reaction = request.POST.get("reaction")
        if reaction == "like":
            reaction = "L"
        elif reaction == "dislike":
            reaction = "D"
        user_review_reaction, *_ = review.userreviewreaction_set.get_or_create(user=request.user)
        if user_review_reaction.reaction == reaction:
            user_review_reaction.reaction = None
        else:
            user_review_reaction.reaction = reaction
        user_review_reaction.save()

    return redirect(request.META["HTTP_REFERER"])


class UserListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5
    queryset = (
        get_user_model().objects.prefetch_related("reviews")
        .annotate(reviews_amount=Count("*"))
    )


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = (
        get_user_model().objects.prefetch_related("reviews")
    )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user_reviews"] = (
            context["object"].reviews.select_related("hotel", "author")
            .prefetch_related("reacted_by").annotate(
                like_amount=Count("userreviewreaction",
                                  filter=Q(userreviewreaction__reaction="L")),
                dislike_amount=Count("userreviewreaction",
                                     filter=Q(userreviewreaction__reaction="D"))
            )
        )
        return context


class UserCreateView(LoginRequiredMixin, generic.CreateView):
    model = Hotel
    fields = "__all__"
    success_url = reverse_lazy("hotel_review_service:user-list")


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Hotel
    fields = "__all__"
    success_url = reverse_lazy("hotel_review_service:user-list")


class UserDeleteView(LoginRequiredMixin, generic.DetailView):
    model = Hotel
    success_url = reverse_lazy("hotel_review_service:user-list")
