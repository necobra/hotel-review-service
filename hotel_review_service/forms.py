from django import forms

from hotel_review_service.models import Hotel, Placement


class HotelForm(forms.ModelForm):
    country = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    adress = forms.CharField(max_length=255)

    class Meta:
        model = Hotel
        fields = ["name", "hotel_class"]

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs and kwargs["instance"]:
            hotel = kwargs["instance"]
            initial = kwargs["initial"]
            initial["country"] = hotel.placement.country
            initial["city"] = hotel.placement.city
            initial["adress"] = hotel.placement.adress

        super().__init__(*args, **kwargs)


class HotelSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        label="",
    )
