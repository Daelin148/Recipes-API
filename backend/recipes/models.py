import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import (MAX_LEN_INGREDIENT_NAME, MAX_LEN_MEASUREMENT_UNIT,
                        MAX_LEN_RECIPE_NAME, MAX_LEN_TAG_FIELDS,
                        MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT, REGEX_TAG)

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=MAX_LEN_TAG_FIELDS, verbose_name='Название', unique=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LEN_TAG_FIELDS,
        verbose_name='Слаг',
        validators=(RegexValidator(regex=REGEX_TAG),))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=MAX_LEN_INGREDIENT_NAME, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LEN_MEASUREMENT_UNIT, verbose_name='Единица измерения'
    )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}.'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=MAX_LEN_RECIPE_NAME, verbose_name='Название',
        blank=False,
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='recipes'
    )
    text = models.TextField('Текстовое описание', blank=False, null=False)
    tags = models.ManyToManyField(Tag, verbose_name='Тэги', blank=False)
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингридиенты', through='RecipeIngredient',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(MinValueValidator(MIN_COOKING_TIME),),
        blank=False,
        null=False
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        default=None,
        blank=False
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User, verbose_name='Пользователь', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Пользователь: {self.user}, Рецепт: {self.recipe}'

    class Meta:
        verbose_name = 'Избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователей'
        default_related_name = 'favorite'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_user_favorite_recipe'
            ),
        )


class RecipeIngredient(models.Model):
    """Модель ингредиентов конкретного рецепта."""

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE
    )
    amount = models.SmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        default_related_name = 'recipeingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_recipe'
            ),
        )


class ShoppingCart(models.Model):
    """Модель корзины покупок."""

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, verbose_name='Пользователь', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_shopping_cart_recipe'
            ),
        )


class ShortLink(models.Model):
    """Модель для хранения коротких ссылок на рецепты."""

    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE,
        related_name='short_link', verbose_name='Рецепт'
    )
    short_link = models.CharField(
        max_length=3, unique=True,
        blank=True, null=True, verbose_name='Короткая ссылка'
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткиу ссылки'

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = self.generate_short_link()
        super().save(*args, **kwargs)

    def generate_short_link(self):
        """Генерирует уникальную короткую ссылку."""

        length = 3
        characters = string.ascii_letters + string.digits
        while True:
            short_link = ''.join(random.choices(characters, k=length))
            if not ShortLink.objects.filter(short_link=short_link).exists():
                break
        return short_link
