from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status, viewsets, filters
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from recipes.pagination import CustomPageNumberPagination
from .filters import IngredientSearchFilter, RecipeFilter
from .models import Ingredient, Tag, Recipe, IngredientAmountInRecipe, Favorite, ShoppingCart
from users.models import CustomUser
from users.serializers import ShortRecipesSerializer
from users.permissions import AdminOrReadOnly, AuthorOrReadOnly
from .serializers import IngredientSerializer, TagSerializer, RecipeReadSerializer, RecipeWriteSerializer

User = CustomUser


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = RecipeFilter
   

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, pk)
        return None

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe=pk).exists():
            return Response({
                'errors': 'Ошибка - Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe=pk)
        if not obj.exists():
            return Response({
                'errors': 'Ошибка - Рецепт уже удален'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
