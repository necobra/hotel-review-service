from django import forms


class HotelSearchForm(forms.Form):
    hotel_name = forms.CharField(
        max_length=255,
        required=False,
        label="",
    )
