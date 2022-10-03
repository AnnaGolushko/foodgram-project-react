from django.contrib import admin

from .models import CustomUser, Subscribe


class CustomUserAdmin(admin.ModelAdmin):
    """Настрока панели администратора для модели CustomUser."""
    list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')


class SubscribeAdmin(admin.ModelAdmin):
    """Настрока панели администратора для модели Subscribe."""
    list_display = ('pk', 'user', 'author')
    search_fields = ('user__username', 'author__username')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
