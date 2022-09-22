from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from drf_base64.fields import Base64ImageField
from django.db.models import F

from users.serializers import CustomUserListSerializer
from users.models import CustomUser, Subscribe

from .models import Ingredient, Tag, Recipe, IngredientAmountInRecipe, Favorite, ShoppingCart


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit'] 


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


# class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='ingredient.id')
#     name = serializers.CharField(source='ingredient.name')
#     measurement_unit = serializers.CharField(
#         source='ingredient.measurement_unit'
#     )
#     amount = serializers.IntegerField()

#     class Meta:
#         model = IngredientAmountInRecipe
#         fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        # но осталось непонятно почему я здесь эту модель указываю? amount это поле этой модели. 
        # Но ведь этот сериализатор не знает что за ID мы даем ему. Для него это просто число. Или нет?
        model = IngredientAmountInRecipe
        # эти поля указываем потому что они будут переданы через API.
        # Далее перед сохранением поля будут обработаны методом create Рецепта
        # и там записаны напрямую в модель IngredientAmountInRecipe
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

    # def validate(self, data):
    #     ingredients = data['ingredients']
    #     ingredient_list = []
    #     for items in ingredients:
    #         ingredient = get_object_or_404(
    #             Ingredient, id=items['id'])
    #         if ingredient in ingredient_list:
    #             raise serializers.ValidationError(
    #                 'Ингредиент должен быть уникальным!'
    #             )
    #         ingredient_list.append(ingredient)
    #     tags = data['tags']
    #     if not tags:
    #         raise serializers.ValidationError(
    #             'Нужен хотя бы один тэг для рецепта!'
    #         )
    #     for tag_name in tags:
    #         if not Tag.objects.filter(name=tag_name).exists():
    #             raise serializers.ValidationError(
    #                 f'Тэга {tag_name} не существует!'
    #             )
    #     return data

    # def validate_cooking_time(self, cooking_time):
    #     if int(cooking_time) < 1:
    #         raise serializers.ValidationError('Время приготовления >= 1!')
    #     return cooking_time

    # def validate_ingredients(self, ingredients):
    #     if not ingredients:
    #         raise serializers.ValidationError('Мин. 1 ингредиент в рецепте!')
    #     for ingredient in ingredients:
    #         if int(ingredient.get('amount')) < 1:
    #             raise serializers.ValidationError(
    #                 'Количество ингредиента >= 1!'
    #             )
    #     return ingredients


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserListSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = serializers.SerializerMethodField()
    # ingredients = RecipeIngredientsReadSerializer(
    #     many=True, read_only=True, source='ingredientamount_set'
    # )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time']

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(
            user=user_id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=user_id, recipe=obj.id).exists()
