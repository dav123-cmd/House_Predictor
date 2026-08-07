from django.db import models


class PredictionHistory(models.Model):
    """Stores every prediction made, so users can see past estimates."""
    area = models.FloatField(help_text="Area in square feet")
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    age = models.FloatField(help_text="Age of property in years")
    location_score = models.FloatField(help_text="Location desirability, 1-10")
    predicted_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"${self.predicted_price:,.0f} ({self.area} sqft, {self.created_at:%Y-%m-%d %H:%M})"
