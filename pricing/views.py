from django.shortcuts import render
from .forms import PricingForm
from .models import PredictionHistory
from .ml.predictor import predict_price


def predict_view(request):
    predicted_price = None
    error = None

    if request.method == 'POST':
        form = PricingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                predicted_price = predict_price(
                    area=data['area'],
                    bedrooms=data['bedrooms'],
                    bathrooms=data['bathrooms'],
                    age=data['age'],
                    location_score=data['location_score'],
                )
                PredictionHistory.objects.create(
                    area=data['area'],
                    bedrooms=data['bedrooms'],
                    bathrooms=data['bathrooms'],
                    age=data['age'],
                    location_score=data['location_score'],
                    predicted_price=predicted_price,
                )
            except FileNotFoundError as e:
                error = str(e)
    else:
        form = PricingForm()

    history = PredictionHistory.objects.all()[:8]

    context = {
        'form': form,
        'predicted_price': predicted_price,
        'error': error,
        'history': history,
    }
    return render(request, 'pricing/home.html', context)
