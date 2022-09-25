from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Sum
from rest_framework import status, viewsets, filters
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from recipes.pagination import CustomPageNumberPagination
from .filters import IngredientSearchFilter, RecipeFilter
from .models import Ingredient, Tag, Recipe, IngredientAmountInRecipe, Favorite, ShoppingCart
from users.models import CustomUser
from users.serializers import ShortRecipesSerializer
from users.permissions import AdminOrReadOnly, AuthenticatedOrAuthorOrReadOnly
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
    permission_classes = (AuthenticatedOrAuthorOrReadOnly,)
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_new_object(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_existing_object(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_new_object(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_existing_object(ShoppingCart, request.user, pk)
        return None

    def add_new_object(self, model, user, pk):
        if model.objects.filter(user=user, recipe=pk).exists():
            return Response({
                'errors': 'Ошибка - Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_existing_object(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe=pk)
        if not obj.exists():
            return Response({
                'errors': 'Ошибка - Рецепт уже удален'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        shopping_list = IngredientAmountInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            'ingredients__name',
            'ingredients__measurement_unit').annotate(amount=Sum('amount')).order_by()
        
        content = (
            [f'{item["ingredients__name"]} ({item["ingredients__measurement_unit"]}) '
            f'- {item["amount"]}\n'
            for item in shopping_list]
        )
        filename = 'shopping_list.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response
