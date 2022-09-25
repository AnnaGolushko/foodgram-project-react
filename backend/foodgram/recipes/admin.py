from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmountInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    """Настрока панели администратора для модели Ingredient."""
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Настрока панели администратора для модели Tag."""
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Настрока панели администратора для модели Recipe."""
    list_display = ('pk', 'name', 'text', 'author', 'image', 'favorited_count')
    list_editable = ('name', 'text', 'author', 'image')
    exclude = ('ingredients',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__username', 'name', 'tags__name')

    def favorited_count(self, obj):
        return Favorite.objects.filter(recipe=obj.id).count()


class IngredientAmountInRecipeAdmin(admin.ModelAdmin):
    """Настрока панели администратора для модели IngredientAmountInRecipe."""
    list_display = ('pk', 'recipe', 'ingredients', 'amount')
    search_fields = ('recipe__name', 'ingredients__name')


class FavoriteShoppingCartAdmin(admin.ModelAdmin):
    """Настрока панели администратора для моделей Favorite и ShoppingCart."""
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteShoppingCartAdmin)
admin.site.register(ShoppingCart, FavoriteShoppingCartAdmin)
admin.site.register(IngredientAmountInRecipe, IngredientAmountInRecipeAdmin)
