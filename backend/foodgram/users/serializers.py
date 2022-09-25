from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import CustomUser, Subscribe
from recipes.models import Recipe


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')

 
class CustomUserListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    # метод получения поля is_subscribed в этой ситуации отличается от SubscribeSerializer,
    # потому что здесь obj - CustomUser, а там obj - Subscribe (судя по ошибкам которые получала)
    def get_is_subscribed(self, obj): # эту часть кода необходимо будет вынести в отдельный класс, но как?
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()
        # return user.follower.filter(author=obj.id).exists() - альтернатива через related_name


class ShortRecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
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
        return Subscribe.objects.filter(user=user, author=obj.author.id).exists()

    def get_recipes_count(self, obj):
        # в obj получаем объект модели Subscribe, поскольку во ViewSet сохраняем Subscibe-подписки через этот сериализатор
        person = obj.author.id
        return Recipe.objects.filter(author=person).count()

    def to_representation(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        response = super().to_representation(obj)
        response['recipes'] = response['recipes'][:int(recipes_limit)]
        return response
