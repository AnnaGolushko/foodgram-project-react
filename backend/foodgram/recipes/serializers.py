from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField

from users.serializers import CustomUserListSerializer

from .models import Ingredient, Tag, Recipe, IngredientAmountInRecipe, Favorite, ShoppingCart


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit'] 


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientAmountInRecipe
        fields = ['id', 'amount'] 


class RecipeWriteSerializer(serializers.ModelSerializer):
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
        for ingredient in ingredients:
            IngredientAmountInRecipe.objects.create(
                recipe=recipe,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'))
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        # если не проделывать это действие то теги и так нормально пересохранятся из validated_data.
        # Стоит ли принудительно это проделывать для явности?
        instance.tags.set(validated_data.pop('tags'))
        for ingredient in ingredients:
            IngredientAmountInRecipe.objects.create(
                recipe=instance,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'))
        
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientAmountInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
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
