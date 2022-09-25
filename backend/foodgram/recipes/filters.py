from django_filters import AllValuesMultipleFilter, rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(method='favorite')
    is_in_shopping_cart = rest_framework.BooleanFilter(method='shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    author = AllValuesMultipleFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def favorite(self, queryset, name, value):
        # если в запросе передано ?is_favorited=1, то выбираем
        # записи из таблицы Favorite по related_name usera
        # т.е. ищем записи где текущий пользователь добавил в избранное рецепты
        if value is True:
            queryset = queryset.filter(
                favorites__user__username=self.request.user
            )
            return queryset
        # # если в запросе передано ?is_favorited=0, то наоборот,
        # но не понятно а зачем этот случай.
        # сделала, потому что в документации к API это требуется.
        # но для интерфейса не понимаю зачем оно...
        elif value is False:
            queryset = queryset.exclude(
                favorites__user__username=self.request.user
            )
            return queryset

    def shopping_cart(self, queryset, name, value):
        if value is True:
            queryset = queryset.filter(
                shopping_cart__user__username=self.request.user
            )
            return queryset
        elif value is False:
            queryset = queryset.exclude(
                shopping_cart__user__username=self.request.user
            )
            return queryset
