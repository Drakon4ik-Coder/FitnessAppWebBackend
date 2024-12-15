# serializers.py
from rest_framework import serializers
from .models import Food, EatenFood

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class EatenFoodSerializer(serializers.ModelSerializer):
    food = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all())
    food_name = serializers.CharField(source='food.name', read_only=True)
    calories = serializers.SerializerMethodField()

    def get_calories(self, obj):
        return (obj.food.calories * obj.weight) / 100

    class Meta:
        model = EatenFood
        fields = ['id', 'food', 'weight', 'timestamp', 'food_name', 'calories']