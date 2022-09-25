from django.db import models
from users.models import CustomUser
from django.core import validators


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
        ordering = ['name']
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
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_color'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления блюда по рецепту (мин.)',
        validators=[validators.MinValueValidator(
            1, message='Минимальное время приготовления 1 минута'),
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient, 
        through='IngredientAmountInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег рецепта'
        )

    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientAmountInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт для указания ингредиентов',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipe',
        verbose_name='Связанные ингредиенты'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[validators.MinValueValidator(
            1, message='Количество ингредиента в рецепте необходимо не менее 1 (г., мл., щепоток и т.д.')]
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredients'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'ID {self.id} - Рецепт <{self.recipe.name}> - Ингредиент <{self.ingredients.name}> - Кол-во <{self.amount}> '


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт в списке избранного',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт в списке покупок',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_user_shopping_cart'
            )
        ]
