from django import forms

from hotel_review_service.models import Hotel, Placement


class HotelForm(forms.ModelForm):
    country = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    adress = forms.CharField(max_length=255)

    class Meta:
        model = Hotel
        fields = ["name", "hotel_class"]


class HotelSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        label="",
    )
