from django import forms
from .models import Listing

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image_url", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "starting_bid": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "image_url": forms.URLInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
