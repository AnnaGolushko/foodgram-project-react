import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Управляющая команда для загрузки Ингрединетов из файла json."""

    def handle(self, *args, **options):
        try:
            with open('/data/ingredients.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ingredient in data:
                    try:
                        Ingredient.objects.create(
                            name=ingredient["name"],
                            measurement_unit=ingredient["measurement_unit"]
                        )
                    except IntegrityError:
                        print(f'Ингридиет {ingredient["name"]} '
                              f'уже есть в базе'
                        )

        except FileNotFoundError:
            raise CommandError('Файл отсутствует в директории data')
