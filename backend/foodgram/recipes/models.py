from django.db import models

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=150,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        max_length=25
    )

    class Meta:
        # ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_for_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='HEX-код',
        unique=True
    )
    slug = models.SlugField(
        max_length=30,
        unique=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_color'
            )
        ]

    def __str__(self):
        return self.name
