from django.db import models
from django.contrib.auth.models import User

class DailyMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    morning_meal = models.CharField(max_length=255)
    morning_quantity = models.PositiveIntegerField()
    evening_meal = models.CharField(max_length=255)
    evening_quantity = models.PositiveIntegerField()
    dinner_meal = models.CharField(max_length=255)
    dinner_quantity = models.PositiveIntegerField()
    summary = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
