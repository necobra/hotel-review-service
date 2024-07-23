from django.urls import path

from hotel_review_service.views import (
    UserListView,
    UserDetailView,
    ReviewListView,
    ReviewDetailView,
    ReviewUpdateView,
    ReviewDeleteView,
    ReviewCreateView,
    HotelListView,
    HotelDetailView,
    HotelUpdateView,
    HotelDeleteView,
    HotelCreateView,
    index,
    review_rate
)


urlpatterns = [
    path("",
         index,
         name="index"),
    path("users/",
         UserListView.as_view(),
         name="user-list"),
    path("users/<int:pk>/",
         UserDetailView.as_view(),
         name="user-detail"),

    path("reviews/",
         ReviewListView.as_view(),
         name="review-list"),
    path("reviews/<int:pk>/",
         ReviewDetailView.as_view(),
         name="review-detail"),
    path("reviews/create/<int:pk>/",
         ReviewCreateView.as_view(),
         name="review-create"),
    path("reviews/<int:pk>/update",
         ReviewUpdateView.as_view(),
         name="review-update"),
    path("reviews/<int:pk>/delete",
         ReviewDeleteView.as_view(),
         name="review-delete"),

    path("reviews/<int:pk>/rate",
         review_rate,
         name="review-rate"),

    path("hotels/",
         HotelListView.as_view(),
         name="hotel-list"),
    path("hotels/<int:pk>/",
         HotelDetailView.as_view(),
         name="hotel-detail"),
    path("hotels/create/",
         HotelCreateView.as_view(),
         name="hotel-create"),
    path("hotels/<int:pk>/update",
         HotelUpdateView.as_view(),
         name="hotel-update"),
    path("hotels/<int:pk>/delete",
         HotelDeleteView.as_view(),
         name="hotel-delete"),
]

app_name = "hotel_review_service"
