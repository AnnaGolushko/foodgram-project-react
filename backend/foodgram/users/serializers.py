# from django.shortcuts import get_object_or_404
# from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework import serializers

from users.models import CustomUser, Subscribe


class CustomUserCreateSerializer(UserCreateSerializer):
    """Переопределение встроенного сериализатора создания пользователя.
    Необходим для обработки всех обязательных для ввода полей."""

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')


class CustomUserListSerializer(UserSerializer):
    """Переопределение встроенного сериализатора чтения информации о пользователях.
    В response добавляется дополнительное вычисляемое поле 'is_subscribed'."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()
        # альтернатива через related_name
        # return user.follower.filter(author=obj.id).exists()


class ShortRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe с краткой информацией о рецептах.
    Применяется для сериализатора подписок пользователей."""

    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки пользователей друг на друга.
    Записи создаются в модели Subscribe.
    В response добавляются вычисляемые поля is_subscribed и recipes_count.
    В response также добавляются recipes из модели Recipe."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShortRecipesSerializer(source='author.recipes',
                                     read_only=True,
                                     many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, author=obj.author.id
        ).exists()

    def get_recipes_count(self, obj):
        # в obj получаем объект модели Subscribe, поскольку
        # во ViewSet сохраняем Subscibe-подписки через этот сериализатор
        person = obj.author.id
        return Recipe.objects.filter(author=person).count()

    def to_representation(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if not recipes_limit:
            return super().to_representation(obj)

        response = super().to_representation(obj)
        response['recipes'] = response['recipes'][:int(recipes_limit)]
        return response


class SubscribeWriteDeleteSerializer(serializers.ModelSerializer):
    queryset = CustomUser.objects.all()
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        required=True,
        slug_field='username',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        request = self.context.get('request')
        author = data['author']

        if request.method == 'POST':
            if request.user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя'
                )
            if Subscribe.objects.filter(
                user=request.user, author=author
            ).exists():
                raise serializers.ValidationError(
                    'Подписка на этого автора уже есть'
                )
        if request.method == 'DELETE':
            if request.user == author:
                raise serializers.ValidationError(
                    'Нельзя отписаться от себя'
                )
            if not Subscribe.objects.filter(
                user=request.user, author=author
            ).exists():
                raise serializers.ValidationError(
                    'подписка на этого автора отсутствует'
                )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        author = validated_data['author']
        Subscribe.objects.get_or_create(user=user, author=author)
        return validated_data
