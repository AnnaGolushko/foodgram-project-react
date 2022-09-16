# from api.filters import IngredientFilter, RecipeFilter
# from django.db.models.aggregates import Count, Sum
# from django.shortcuts import get_object_or_404

# from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
#                             Subscribe, Tag)
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
# from rest_framework.decorators import action, api_view
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from djoser.views import UserViewSet
from djoser.conf import settings

from users.models import CustomUser
from api.serializers import CustomUserCreateSerializer, CustomUserListSerializer

User = CustomUser


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == "set_password":
            return settings.SERIALIZERS.set_password
        elif self.request.method == 'GET':
            return CustomUserListSerializer

    # def perform_create(self, serializer):
    #     password = make_password(self.request.data['password'])
    #     serializer.save(password=password)

    # @action(detail=False, permission_classes=(IsAuthenticated,))
    # def subscriptions(self, request):
    #     user = request.user
    #     queryset = Subscribe.objects.filter(user=user)
    #     pages = self.paginate_queryset(queryset)
    #     serializer = SubscribeSerializer(
    #         pages, many=True, context={'request': request}
    #     )
    #     return self.get_paginated_response(serializer.data)