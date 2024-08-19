from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import MAX_LENGTH_CHARFIELD, MAX_LENGTH_EMAIL
from users.validators import validate_username


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        verbose_name='Имя пользователя',
        unique=True,
        blank=False,
        null=False,
        validators=(validate_username,))

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта',
        unique=True,
        blank=False,
        null=False,
    )

    first_name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        verbose_name='Имя',
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        verbose_name='Фамилия',
        blank=False,
        null=False,
    )
    password = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        verbose_name='Пароль',
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='username_email_unique'
            ),
        )

    def __str__(self):
        return self.username


class Follower(models.Model):
    """Модель подписки на других пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='user_author_unique'
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
