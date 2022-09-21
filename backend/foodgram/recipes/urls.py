from django.urls import include, path
from rest_framework.routers import DefaultRouter
from recipes.views import IngredientsViewSet, TagsViewSet, RecipeViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
               path('', include(router.urls)),
               ]
