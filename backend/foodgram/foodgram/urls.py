from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls', namespace='users')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('recipes.urls', namespace='recipes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
