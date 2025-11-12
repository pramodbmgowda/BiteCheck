from django import forms
from .models import DailyMeal

class DailyMealForm(forms.ModelForm):
    class Meta:
        model = DailyMeal
        fields = [
            'morning_meal', 'morning_quantity',
            'evening_meal', 'evening_quantity',
            'dinner_meal', 'dinner_quantity'
        ]
