from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.db.models import UniqueConstraint

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

    @property
    def average_rating(self) -> float:
        average = self.reviews.aggregate(
            hotel_rating=models.Avg("hotel_rating")
        ).get("hotel_rating")
        return round(average, 1) if average is not None else 0.0

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} {self.hotel_class} {self.placement}"


class User(AbstractUser):
    @property
    def reviews_amount(self) -> int:
        return self.reviews.count()

    @property
    def liked(self) -> list["Review"]:
        return [
            reviewuser.review for reviewuser in self.reviewuser_set.filter(action="L")
        ]

    @property
    def disliked(self) -> list["Review"]:
        return [
            reviewuser.review for reviewuser in self.reviewuser_set.filter(action="D")
        ]

    class Meta:
        ordering = ("first_name", "last_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Review(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        through="ReviewUser",
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
        return self.likes - self.dislikes

    @property
    def likes(self) -> int:
        return self.reviewuser_set.filter(action="L").count()

    @property
    def dislikes(self) -> int:
        return self.reviewuser_set.filter(action="D").count()

    @property
    def author(self) -> settings.AUTH_USER_MODEL:
        return self.reviewuser_set.get(action="A").user

    class Meta:
        # todo make order by likes
        ordering = ("caption",)

    def __str__(self) -> str:
        return self.caption


class ReviewUser(models.Model):
    actions = (
        ("A", "Author"),
        ("L", "Liked"),
        ("D", "Disliked")
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=actions, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "review"), name="unique_user_review")
        ]
