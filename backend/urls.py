# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from FitnessApp.views import ItemListCreateView, ItemDetailView, RecipeListCreateView, ActionDeleteView, \
    ActionListCreateView, CustomTokenObtainPairView, UserRegistrationView, AvailableIngredientsView, EatenFoodView, \
    ItemIngredientsView, MealRecommendationsView, UserSettingsView

urlpatterns = [
    path('items/', ItemListCreateView.as_view(), name='item_list_create'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('items/<int:item_id>/ingredients/', ItemIngredientsView.as_view(), name='item_ingredients'),

    path('recipes/', RecipeListCreateView.as_view(), name='recipe_list_create'),
    path('actions/', ActionListCreateView.as_view(), name='action_list_create'),
    path('actions/<int:pk>/', ActionDeleteView.as_view(), name='action_delete'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', UserRegistrationView.as_view(), name='user_registration'),
    path('user-settings/', UserSettingsView.as_view(), name='user_settings'),
    path('available-ingredients/', AvailableIngredientsView.as_view(), name='available_ingredients'),
    path('eaten-food/', EatenFoodView.as_view(), name='eaten_food'),
    path('meal-recommendations/', MealRecommendationsView.as_view(), name='meal_recommendations'),

]