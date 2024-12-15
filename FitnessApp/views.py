# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Food, EatenFood
from .serializers import FoodSerializer, EatenFoodSerializer

class FoodListAPIView(APIView):
    def get(self, request):
        foods = Food.objects.all()
        serializer = FoodSerializer(foods, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FoodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EatenFoodListAPIView(APIView):
    def get(self, request):
        eaten_foods = EatenFood.objects.all()
        serializer = EatenFoodSerializer(eaten_foods, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EatenFoodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            eaten_food = EatenFood.objects.get(pk=pk)
            eaten_food.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EatenFood.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
