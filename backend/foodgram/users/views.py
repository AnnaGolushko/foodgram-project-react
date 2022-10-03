from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.pagination import CustomPageNumberPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import CustomUser, Subscribe
from users.serializers import (CustomUserCreateSerializer,
                               CustomUserListSerializer, SubscribeSerializer,
                               SubscribeWriteDeleteSerializer)

User = CustomUser


class CustomUserViewSet(UserViewSet):
    """Переопределение встроенного представления пользователя.
    Добавлены эндпоинты для функции подписки пользователей друг на друга."""

    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.request.method == 'GET':
            return CustomUserListSerializer

        return UserViewSet.get_serializer_class(self)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscribeWriteDeleteSerializer(
            data={'user': request.user, 'author': author},
            context={'request': request}
        )

        if self.request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            new_subscription = Subscribe.objects.create(
                user=user, author=author
            )
            serializer = SubscribeSerializer(
                new_subscription, context={'request': request}
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            serializer.is_valid(raise_exception=True)
            subscription = Subscribe.objects.filter(
                user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
