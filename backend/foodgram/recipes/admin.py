from django.contrib import admin
from .models import Ingredient, Tag


admin.site.register(Ingredient)
admin.site.register(Tag)
