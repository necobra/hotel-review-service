from django.db.models import Manager, QuerySet, Count, Q


def get_reviews_with_calculated_fields(reviews: Manager) -> QuerySet:
    return (
        reviews.select_related("hotel", "author")
        .prefetch_related("reacted_by").annotate(
            like_amount=Count("userreviewreaction",
                              filter=Q(userreviewreaction__reaction="L")),
            dislike_amount=Count("userreviewreaction",
                                 filter=Q(userreviewreaction__reaction="D"))
        )).order_by("-created_at")
