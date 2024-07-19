from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models

from core import settings


class HotelClass(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name


class Placement(models.Model):
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    adress = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.country}, {self.city}, {self.adress}"


class Hotel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    placement = models.OneToOneField(
        Placement, on_delete=models.CASCADE
    )
    hotel_class = models.ForeignKey(
        HotelClass, on_delete=models.DO_NOTHING, related_name="hotels"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} {self.hotel_class} {self.placement}"


class User(AbstractUser):
    reviews_reacted = models.ManyToManyField(
        "Review",
        through="UserReviewReaction",
        related_name="reacted_by"
    )

    @property
    def liked(self) -> list["Review"]:
        return [
            user_reactions.review for user_reactions in self.userreviewreaction_set.filter(reaction="L")
        ]

    @property
    def disliked(self) -> list["Review"]:
        return [
            user_reactions.review for user_reactions in self.userreviewreaction_set.filter(reaction="D")
        ]

    class Meta:
        ordering = ("first_name", "last_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Review(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    caption = models.CharField(max_length=255)
    comment = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    hotel_rating = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(10)
        ]
    )

    @property
    def review_rating(self) -> int:
        return self.like_amount - self.dislike_amount

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.caption


class UserReviewReaction(models.Model):
    reactions = (
        ("L", "Liked"),
        ("D", "Disliked")
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=1, choices=reactions, null=True)
