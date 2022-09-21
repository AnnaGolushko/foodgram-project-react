# from api.filters import IngredientFilter, RecipeFilter
# from django.db.models.aggregates import Count, Sum
from django.shortcuts import get_object_or_404
from django.http import Http404

# from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
#                             Subscribe, Tag)
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
# from rest_framework.decorators import action, api_view
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Ingredient, Tag, Recipe, IngredientAmountInRecipe
from users.models import CustomUser
from .serializers import IngredientSerializer, TagSerializer, RecipeReadSerializer, RecipeWriteSerializer

User = CustomUser


class IngredientsViewSet(ReadOnlyModelViewSet):
    # permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # filter_backends = (IngredientSearchFilter,)
    # search_fields = ('^name',)


class TagsViewSet(ReadOnlyModelViewSet):
    # permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # pagination_class = LimitPageNumberPagination
    # filter_class = RecipeFilter
    # permission_classes = (AdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)
