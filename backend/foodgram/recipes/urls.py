from django.urls import include, path
from rest_framework.routers import DefaultRouter
from recipes.views import IngredientsViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('ingredients', IngredientsViewSet)

urlpatterns = [
               path('', include(router.urls)),
               ]
