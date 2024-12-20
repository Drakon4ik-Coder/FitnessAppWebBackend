# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework_simplejwt.tokens import AccessToken

from .models import Item, Recipe, Action, UserSettings
from .serializers import ItemSerializer, RecipeSerializer, ActionSerializer, UserRegistrationSerializer, \
    UserSettingsSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserSettingsView(generics.RetrieveUpdateAPIView):
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserSettings.objects.get_or_create(user=self.request.user)[0]

class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemDetailView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(item)
        data = serializer.data
        return Response(data)


class ItemIngredientsView(APIView):
    def get(self, request, item_id, *args, **kwargs):
        try:
            item = Item.objects.get(pk=item_id)
            if not item.is_meal:
                return Response({"detail": "Item is not a meal."}, status=status.HTTP_400_BAD_REQUEST)

            recipes = Recipe.objects.filter(meal=item)
            ingredients = [
                {
                    "ingredient_id": recipe.ingredient.item_id,
                    "name": recipe.ingredient.name,
                    "quantity": recipe.quantity
                }
                for recipe in recipes
            ]
            return Response(ingredients, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        recipe = serializer.save()
        meal = recipe.meal
        meal_nutrition = meal.get_nutrition()
        meal.calories = meal_nutrition['calories']
        meal.serving_weight = meal_nutrition['serving_weight']
        meal.protein = meal_nutrition['protein']
        meal.fats_saturated = meal_nutrition['fats_saturated']
        meal.fats_unsaturated = meal_nutrition['fats_unsaturated']
        meal.carbs_sugar = meal_nutrition['carbs_sugar']
        meal.carbs_fiber = meal_nutrition['carbs_fiber']
        meal.carbs_starch = meal_nutrition['carbs_starch']
        meal.save()

class ActionListCreateView(generics.ListCreateAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ActionDeleteView(generics.DestroyAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated]

class AvailableIngredientsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        action = Action.objects.filter(user=user).first()
        if action:
            available_ingredients = action.get_available_ingredients()
            return Response(available_ingredients, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

class EatenFoodView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        action = Action.objects.filter(user=user).first()
        if action:
            eaten_food = action.get_eaten_food()
            return Response(eaten_food, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

class MealRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        action = Action.objects.filter(user=user).first()
        if not action:
            return Response({"detail": "No actions found for the user."}, status=status.HTTP_404_NOT_FOUND)

        available_ingredients = action.get_available_ingredients()
        available_ingredient_ids = available_ingredients.keys()

        recommended_meals = Item.objects.filter(
            is_meal=True,
            meal_recipes__ingredient__item_id__in=available_ingredient_ids
        ).distinct()

        valid_meals = []
        for meal in recommended_meals:
            recipes = Recipe.objects.filter(meal=meal)
            fail = False
            for recipe in recipes:
                if recipe.ingredient.item_id not in available_ingredients.keys():
                    fail = True
            if fail:
                continue
            if all(available_ingredients[recipe.ingredient.item_id] >= recipe.quantity for recipe in recipes):
                valid_meals.append(meal)

        if not valid_meals:
            return Response({"detail": "No valid meal recommendations found."}, status=status.HTTP_204_NO_CONTENT)

        serializer = ItemSerializer(valid_meals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)