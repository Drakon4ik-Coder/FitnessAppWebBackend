# models.py
from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    fats = models.FloatField(default=0.0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class EatenFood(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='eaten_foods')
    weight = models.FloatField(default=100)  # Portion size in grams
    timestamp = models.DateTimeField(auto_now_add=True)
