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

    def get_is_subscribed(self, obj): # эту часть кода необходимо будет вынести в отдельный класс
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        # return Subscribe.objects.filter(user=user, author=obj.id).exists()
        return user.follower.filter(author=obj.id).exists()

class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    # recipes_count = serializers.SerializerMethodField('get_recipes_count')
    # username = serializers.CharField(
    #     required=True,
    #     validators=[validators.UniqueValidator(
    #         queryset=CustomUser.objects.all()
    #     )]
    # )

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
        return user.follower.filter(author=obj.id).exists()

    # def validate(self, data):
    #     author = data['followed']
    #     user = data['follower']
    #     if user == author:
    #         raise serializers.ValidationError('You can`t follow for yourself!')
    #     if (Follow.objects.filter(author=author, user=user).exists()):
    #         raise serializers.ValidationError('You have already subscribed!')
    #     return data

    # def create(self, validated_data):
    #     subscribe = Follow.objects.create(**validated_data)
    #     subscribe.save()
    #     return subscribe

    def get_recipes(self, data):
        return 1
        # recipes_limit = self.context.get('request').GET.get('recipes_limit')
        # recipes = (
        #     data.recipes.all()[:int(recipes_limit)]
        #     if recipes_limit else data.recipes
        # )
        # serializer = serializers.ListSerializer(child=RecipeSerializer())
        # return serializer.to_representation(recipes)

    def get_recipes_count(self, data):
        return 2
        # return Recipe.objects.filter(author=data).count()










# class CustomUserCreateSerializer(UserCreateSerializer):
#     # email = serializers.EmailField(
#     #     validators=[UniqueValidator(queryset=User.objects.all())])
#     # username = serializers.CharField(
#     #     validators=[UniqueValidator(queryset=User.objects.all())])

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'password', 'username', 'first_name', 'last_name')
#         # extra_kwargs = {
#         #     'email': {'required': True},
#         #     'username': {'required': True},
#         #     'password': {'required': True},
#         #     'first_name': {'required': True},
#         #     'last_name': {'required': True},
#         # }
