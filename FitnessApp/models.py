# models.py
from django.db import models
from django.contrib.auth.models import User

class Food(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    fats = models.FloatField(default=0.0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class EatenFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    weight = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)