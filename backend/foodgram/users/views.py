from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from djoser.conf import settings

from recipes.pagination import CustomPageNumberPagination
from users.models import CustomUser, Subscribe
from users.serializers import CustomUserCreateSerializer, CustomUserListSerializer, SubscribeSerializer

User = CustomUser


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == "set_password":
            return settings.SERIALIZERS.set_password
        elif self.request.method == 'GET':
            return CustomUserListSerializer
        
        return UserViewSet.get_serializer_class(self)

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=[IsAuthenticated])
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
                    'errors': 'Ошибка - подписка на этого автора уже существует'
                }, status=status.HTTP_400_BAD_REQUEST)

            new_subscription = Subscribe.objects.create(user=user, author=author)
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

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
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
