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
