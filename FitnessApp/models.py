# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.aggregates import Sum

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal_calories = models.IntegerField(default=2000)
    goal_protein = models.FloatField(default=150)
    goal_carbs = models.FloatField(default=250)
    goal_fats = models.FloatField(default=45)

    def __str__(self):
        return f"{self.user.username}'s settings"

class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_meal = models.BooleanField(default=False)
    calories = models.IntegerField(default=0)
    serving_weight = models.IntegerField(default=0)  # Changed from serving_size to serving_weight
    protein = models.FloatField(default=0.0)
    fats_saturated = models.FloatField(default=0.0)
    fats_unsaturated = models.FloatField(default=0.0)
    carbs_sugar = models.FloatField(default=0.0)
    carbs_fiber = models.FloatField(default=0.0)
    carbs_starch = models.FloatField(default=0.0)

    def get_nutrition(self):
        if not self.is_meal:
            return {
                'item_id': self.item_id,
                'name': self.name,
                'is_meal': self.is_meal,
                'calories': self.calories,
                'serving_weight': self.serving_weight,
                'protein': self.protein,
                'fats_saturated': self.fats_saturated,
                'fats_unsaturated': self.fats_unsaturated,
                'carbs_sugar': self.carbs_sugar,
                'carbs_fiber': self.carbs_fiber,
                'carbs_starch': self.carbs_starch,
            }

        recipes = Recipe.objects.filter(meal=self)
        aggregated_values = recipes.aggregate(
            total_calories=Sum(F('ingredient__calories') * F('quantity') / F('ingredient__serving_weight')),
            total_weight=Sum('quantity'),
            total_protein=Sum(F('ingredient__protein') * F('quantity') / F('ingredient__serving_weight')),
            total_fats_saturated=Sum(F('ingredient__fats_saturated') * F('quantity') / F('ingredient__serving_weight')),
            total_fats_unsaturated=Sum(F('ingredient__fats_unsaturated') * F('quantity') / F('ingredient__serving_weight')),
            total_carbs_sugar=Sum(F('ingredient__carbs_sugar') * F('quantity') / F('ingredient__serving_weight')),
            total_carbs_fiber=Sum(F('ingredient__carbs_fiber') * F('quantity') / F('ingredient__serving_weight')),
            total_carbs_starch=Sum(F('ingredient__carbs_starch') * F('quantity') / F('ingredient__serving_weight')),
        )

        return {
            'item_id': self.item_id,
            'name': self.name,
            'is_meal': self.is_meal,
            'calories': aggregated_values['total_calories'] or 0,
            'serving_weight': aggregated_values['total_weight'] or 0,
            'protein': aggregated_values['total_protein'] or 0,
            'fats_saturated': aggregated_values['total_fats_saturated'] or 0,
            'fats_unsaturated': aggregated_values['total_fats_unsaturated'] or 0,
            'carbs_sugar': aggregated_values['total_carbs_sugar'] or 0,
            'carbs_fiber': aggregated_values['total_carbs_fiber'] or 0,
            'carbs_starch': aggregated_values['total_carbs_starch'] or 0,
        }


    def __str__(self):
        return self.name

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    meal = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='meal_recipes')
    ingredient = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ingredient_recipes')
    quantity = models.FloatField()  # Quantity in grams

class Action(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'Add'),
        ('COOK', 'Cook'),
        ('EAT', 'Eat'),
        ('DISPOSE', 'Dispose'),
    ]

    action_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='actions_as_item')
    ingredient = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='actions_as_ingredient')
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.FloatField()  # Quantity in grams
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_available_ingredients(self):
        added_foods = Action.objects.filter(user=self.user, action_type__in=['ADD', 'COOK']).values('item').annotate(total_added=Sum('quantity'))
        eaten_disposed_foods = Action.objects.filter(user=self.user, action_type__in=['EAT', 'DISPOSE', 'COOK']).values('ingredient').annotate(total_eaten_disposed=Sum('quantity'))

        available_ingredients = {}
        for added in added_foods:
            item_id = added['item']
            total_added = added['total_added']
            total_eaten_disposed = next((e['total_eaten_disposed'] for e in eaten_disposed_foods if e['ingredient'] == item_id), 0)
            available_quantity = total_added - total_eaten_disposed
            if available_quantity > 0:
                available_ingredients[item_id] = available_quantity

        return available_ingredients

    def get_eaten_food(self):
        eaten_foods = Action.objects.filter(user=self.user, action_type='EAT').values('action_id','item', 'quantity', 'timestamp')

        eaten_food = []
        for eaten in eaten_foods:
            eaten_food.append({
                'action_id': eaten['action_id'],
                'item_id': eaten['item'],
                'quantity': eaten['quantity'],
                'timestamp': eaten['timestamp']
            })

        return eaten_food