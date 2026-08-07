from django import forms


class PricingForm(forms.Form):
    area = forms.FloatField(
        label="Area (sq ft)",
        min_value=100, max_value=20000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1500'})
    )
    bedrooms = forms.IntegerField(
        label="Bedrooms",
        min_value=0, max_value=15,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3'})
    )
    bathrooms = forms.IntegerField(
        label="Bathrooms",
        min_value=0, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2'})
    )
    age = forms.FloatField(
        label="Property Age (years)",
        min_value=0, max_value=150,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5'})
    )
    location_score = forms.FloatField(
        label="Location Score (1-10)",
        min_value=1, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8'})
    )
