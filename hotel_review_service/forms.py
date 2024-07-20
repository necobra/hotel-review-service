from django import forms


class HotelSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        label="",
    )
