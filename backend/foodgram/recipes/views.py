from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.models import CustomUser
from users.permissions import AdminOrReadOnly, AuthenticatedOrAuthorOrReadOnly
from users.serializers import ShortRecipesSerializer

from recipes.pagination import CustomPageNumberPagination

from .filters import IngredientSearchFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientAmountInRecipe, Recipe,
                     ShoppingCart, Tag)
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer,
                          FavoriteSerializer, ShoppingSerializer)

User = CustomUser


class IngredientsViewSet(ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient.
    Изменения разрешены к внесению только администратору."""

    permission_classes = (AdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagsViewSet(ReadOnlyModelViewSet):
    """ViewSet для модели Tag.
    Изменения разрешены к внесению только администратору."""

    permission_classes = (AdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe.
    Подключены кастомные фильтры для запросов по параметрам.
    Созданы эндпоинты для добавления рецепта
    в избранное (favorite) и список покупок (shopping_cart)."""

    permission_classes = (AuthenticatedOrAuthorOrReadOnly,)
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['POST', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        if request.method == 'POST':
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=request.user)
                serializer = ShortRecipesSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if serializer.is_valid(raise_exception=True):
                favorite = get_object_or_404(
                    Favorite, recipe=recipe, user=request.user
                )
                self.perform_destroy(favorite)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'delete'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        if request.method == 'POST':
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=request.user)
                serializer = ShortRecipesSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if serializer.is_valid(raise_exception=True):
                favorite = get_object_or_404(
                    ShoppingCart, recipe=recipe, user=request.user
                )
                self.perform_destroy(favorite)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        """Эндпоинт для скачивания списка ингрединетов
        для рецептов из списка покупок. Формат файла - .txt."""

        user = request.user
        response = IngredientAmountInRecipe.download_shopping_cart(user)
        return response

    # ниже зеленым мой старый код, пока висит здесь до востребования

    # @action(detail=True, methods=['POST', 'DELETE'])
    # def favorite(self, request, pk=None):
    #     if request.method == 'POST':
    #         return self.add_new_object(Favorite, request.user, pk)

    #     return self.delete_existing_object(Favorite, request.user, pk)

    # @action(detail=True, methods=['POST', 'DELETE'])
    # def shopping_cart(self, request, pk=None):
    #     if request.method == 'POST':
    #         return self.add_new_object(ShoppingCart, request.user, pk)

    #     return self.delete_existing_object(ShoppingCart, request.user, pk)

    # def add_new_object(self, model, user, pk):
    #     """Метод для создания новой записи в модели.
    #     Модель должна иметь поля user и recipe."""

    #     if model.objects.filter(user=user, recipe=pk).exists():
    #         return Response({
    #             'errors': 'Ошибка - Рецепт уже добавлен в список'
    #         }, status=status.HTTP_400_BAD_REQUEST)
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     model.objects.create(user=user, recipe=recipe)
    #     serializer = ShortRecipesSerializer(recipe)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete_existing_object(self, model, user, pk):
    #     """Метод для удаления записи из модели.
    #     Модель должна иметь поля user и recipe."""

    #     obj = model.objects.filter(user=user, recipe=pk)
    #     if not obj.exists():
    #         return Response({
    #             'errors': 'Ошибка - Рецепт уже удален'
    #         }, status=status.HTTP_400_BAD_REQUEST)

    #     obj.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
