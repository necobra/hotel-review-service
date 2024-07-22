from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, QuerySet, Manager
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from hotel_review_service.forms import (
    HotelSearchForm,
    HotelForm,
    ReviewSearchForm,
    UserSearchForm,
    ReviewForm,
)
from hotel_review_service.models import (
    Hotel,
    Review,
    Placement
)


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

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "")
        context["search_form"] = HotelSearchForm(
            initial={"search": search}
        )
        return context

    def get_queryset(self) -> QuerySet:
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

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hotel_reviews"] = (
            get_reviews_with_calculated_fields(context["hotel"].reviews)
        )
        return context


class HotelCreateView(LoginRequiredMixin, generic.CreateView):
    model = Hotel
    form_class = HotelForm
    success_url = reverse_lazy("hotel_review_service:hotel-list")

    def form_valid(self, form) -> HttpResponseRedirect:
        hotel = form.save(commit=False)

        contry = form.cleaned_data["country"]
        city = form.cleaned_data["city"]
        adress = form.cleaned_data["adress"]
        placement = Placement.objects.create(country=contry,
                                             city=city,
                                             adress=adress)

        hotel.placement = placement
        hotel.save()

        return super().form_valid(form)


class HotelUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Hotel
    form_class = HotelForm
    success_url = reverse_lazy("hotel_review_service:hotel-list")

    def form_valid(self, form) -> HttpResponseRedirect:
        hotel = form.save(commit=False)

        contry = form.cleaned_data["country"]
        city = form.cleaned_data["city"]
        adress = form.cleaned_data["adress"]
        placement = Placement.objects.create(country=contry,
                                             city=city,
                                             adress=adress)

        hotel.placement.delete()

        hotel.placement = placement
        hotel.save()

        return super().form_valid(form)


class HotelDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Hotel
    success_url = reverse_lazy("hotel_review_service:hotel-list")
    template_name = "hotel_review_service/hotel_confirm_delete.html"


class ReviewListView(LoginRequiredMixin, generic.ListView):
    model = Review

    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "")
        context["search_form"] = ReviewSearchForm(
            initial={"search": search}
        )
        return context

    def get_queryset(self) -> QuerySet:
        queryset = (
            get_reviews_with_calculated_fields(Review.objects)
        )
        form = ReviewSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data["search"]
            return queryset.filter(Q(caption__icontains=search)
                                   | Q(comment__icontains=search))
        return queryset


class ReviewDetailView(LoginRequiredMixin, generic.DetailView):
    model = Review
    queryset = Review.objects.select_related("user", "hotel")


class ReviewCreateView(LoginRequiredMixin, generic.CreateView):
    model = Review
    form_class = ReviewForm
    success_url = reverse_lazy("hotel_review_service:review-list")

    def form_valid(self, form) -> HttpResponseRedirect:
        review = form.save(commit=False)

        review.author = self.request.user
        review.hotel = get_object_or_404(Hotel, id=self.kwargs["pk"])

        review.save()

        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Review
    fields = ["caption", "comment", "hotel_rating"]
    success_url = reverse_lazy("hotel_review_service:review-list")

    template_name = "hotel_review_service/review_confirm_delete.html"


class ReviewDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Review
    success_url = reverse_lazy("hotel_review_service:review-list")


def review_rate(request, pk: int):
    review = get_object_or_404(Review, id=pk)
    if request.method == "POST":
        if review.author == request.user:
            return HttpResponse(status=400)
        reaction = request.POST.get("reaction")
        if reaction == "like":
            reaction = "L"
        elif reaction == "dislike":
            reaction = "D"
        user_review_reaction, *_ = (review.userreviewreaction_set
                                    .get_or_create(user=request.user))
        if user_review_reaction.reaction == reaction:
            user_review_reaction.reaction = None
        else:
            user_review_reaction.reaction = reaction
        user_review_reaction.save()

    return redirect(request.META["HTTP_REFERER"])


class UserListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "")
        context["search_form"] = UserSearchForm(
            initial={"search": search}
        )
        return context

    def get_queryset(self) -> QuerySet:
        queryset = (
            get_user_model().objects.prefetch_related("reviews")
            .annotate(reviews_amount=Count("reviews"))
        )
        form = UserSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data["search"]
            return queryset.filter(Q(first_name__icontains=search)
                                   | Q(last_name__icontains=search))
        return queryset


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = (
        get_user_model().objects.prefetch_related("reviews")
        .annotate(reviews_amount=Count("*"))
    )

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user_reviews"] = (
            get_reviews_with_calculated_fields(context["object"].reviews)
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


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Hotel
    success_url = reverse_lazy("hotel_review_service:user-list")


def get_reviews_with_calculated_fields(reviews: Manager) -> QuerySet:
    return (
        reviews.select_related("hotel", "author")
        .prefetch_related("reacted_by").annotate(
            like_amount=Count("userreviewreaction",
                              filter=Q(userreviewreaction__reaction="L")),
            dislike_amount=Count("userreviewreaction",
                                 filter=Q(userreviewreaction__reaction="D"))
        ))
