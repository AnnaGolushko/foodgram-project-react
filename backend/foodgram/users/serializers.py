from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import CustomUser
from users.models import Subscribe

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

class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
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

    def get_recipes(self, data):
        return 1

    def get_recipes_count(self, data):
        return 2




# recipes_count = serializers.SerializerMethodField('get_recipes_count')
    # def get_recipes(self, data):
    #     recipes_limit = self.context.get('request').GET.get('recipes_limit')
    #     recipes = (
    #         data.recipes.all()[:int(recipes_limit)]
    #         if recipes_limit else data.recipes
    #     )
    #     serializer = serializers.ListSerializer(child=RecipeSerializer())
    #     return serializer.to_representation(recipes)

    # def get_recipes_count(self, data):
    #     return Recipe.objects.filter(author=data).count()