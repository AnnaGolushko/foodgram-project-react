from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint


class CustomUser(AbstractUser):
    """Переопределение модели User от AbstractUser.
    У стандартной модели поля email, first_name, last_name
    имеют параметр blank=True. """

    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Не допускаются: пробел и символы, кроме . @ + - _',
            ),
        ]
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'id',
        'username',
        'first_name',
        'last_name',
    ]


    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribing_to'
    )

    class Meta:
        ordering = ['-id']
        UniqueConstraint(
            fields=['user', 'author'],
            name='unique_subscribing'
        )

    def __str__(self):
        return f' User - {self.user.username}. Subscribed to - {self.author.username}.'
