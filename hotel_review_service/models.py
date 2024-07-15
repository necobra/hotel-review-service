from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


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
        return float(self.reviews.aggregate(models.Avg("rating")).get("rating__avg", 0.0))

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} {self.hotel_class} {self.placement}"

class User(AbstractUser):
    @property
    def reviews_amount(self) -> int:
        return self.reviews.count()

    class Meta:
        ordering = ("first_name", "last_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Review(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name="reviews"
    )
    caption = models.CharField(max_length=255)
    comment = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ("caption",)
        constraints = [
            UniqueConstraint(fields=["user", "hotel"], name="unique_user_hotel_review")
        ]

    def __str__(self) -> str:
        return self.caption
