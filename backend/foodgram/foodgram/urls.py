from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls', namespace='users')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('recipes.urls', namespace='recipes')),
]
