from django.contrib import admin
from .models import PredictionHistory


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'area', 'bedrooms', 'bathrooms', 'age',
                     'location_score', 'predicted_price', 'created_at')
    ordering = ('-created_at',)
