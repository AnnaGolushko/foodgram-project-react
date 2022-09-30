from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserListSerializer

from .models import (Favorite, Ingredient, IngredientAmountInRecipe,
                     Recipe, ShoppingCart, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient. Используются все поля модели."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag. Используются все поля модели."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для записи в модель IngredientAmountInRecipe."""

    id = serializers.IntegerField()

    class Meta:
        model = IngredientAmountInRecipe
        fields = ['id', 'amount']


def ingredient_bulk_creation(recipe, ingredients):
    """Функция создания объектов в базе IngredientAmountInRecipe
    для сериализатора создания рецепта RecipeWriteSerializer."""

    ingredients_for_creation = list()
    for ingredient in ingredients:
        ingredients_for_creation.append(
            IngredientAmountInRecipe(
                recipe=recipe,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'))
            )
    IngredientAmountInRecipe.objects.bulk_create(ingredients_for_creation)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов (модель Recipe)."""

    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientToRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time']
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить минимум один ингредиент'
            )
        ingredient_list = []
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=item['id'])

            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!'
                )
            ingredient_list.append(ingredient)

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        recipe.tags.set(tags)
        ingredient_bulk_creation(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(validated_data.pop('tags'))
        ingredient_bulk_creation(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения из модели IngredientAmountInRecipe
    с выдачей значений полей из связанной модели Ingredient."""

    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientAmountInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для выдачи в response рецептов (модель Recipe).
    Реализованы вычисляемые поля is_favorited и is_in_shopping_cart."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserListSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientsReadSerializer(
        source='ingredient', many=True, required=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time']

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(
            user=user_id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=user_id, recipe=obj.id).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        request = self.context.get('request')
        user = data['user']['id']
        recipe = data['recipe']['id']
        follow = Favorite.objects.filter(user__id=user, recipe__id=recipe)
        if request.method == 'POST':
            if follow.exists():
                raise serializers.ValidationError(
                    {'errors': 'Нельзя добавить повторно рецепт в избранное.'}
                )
        if request.method == 'DELETE':
            if not follow.exists():
                raise serializers.ValidationError(
                    {'errors': 'Нельзя удалить повторно рецепт из избранного.'}
                )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class ShoppingSerializer(FavoriteSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)

    def validate(self, data):
        request = self.context.get('request')
        user = data['user']['id']
        recipe = data['recipe']['id']
        want_to_buy = ShoppingCart.objects.filter(
            user__id=user, recipe__id=recipe
        )
        if request.method == 'POST':
            if want_to_buy.exists():
                raise serializers.ValidationError(
                    {'errors': 'Нельзя добавить повторно рецепт в список.'}
                )
        if request.method == 'DELETE':
            if not want_to_buy.exists():
                raise serializers.ValidationError(
                    {'errors': 'Нельзя удалить повторно рецепт из списка.'}
                )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
