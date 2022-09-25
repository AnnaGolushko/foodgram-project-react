from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.pagination import CustomPageNumberPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import CustomUser, Subscribe
from users.serializers import (CustomUserCreateSerializer,
                               CustomUserListSerializer, SubscribeSerializer)

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

        if self.request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Ошибка - нельзя подписаться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response({
                    'errors': 'Ошибка - подписка на этого автора уже есть'
                }, status=status.HTTP_400_BAD_REQUEST)

            new_subscription = Subscribe.objects.create(
                user=user, author=author
            )
            serializer = SubscribeSerializer(
                new_subscription, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if user == author:
                return Response({
                    'errors': 'Ошибка - нельзя отписаться от самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            subscription = Subscribe.objects.filter(user=user, author=author)
            if not subscription.exists():
                return Response({
                    'errors': 'Ошибка - подписка на этого автора отсутствует'
                }, status=status.HTTP_400_BAD_REQUEST)

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
