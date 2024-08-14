
from django.conf import settings
from djoser.serializers import \
    UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, ShortLink, Tag)
from rest_framework import serializers
from users.models import Follower, User


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для получения пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(use_url=True, read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password', 'avatar')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follower.objects.filter(user=user, author=obj).exists()
        return False


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class AvatarUserSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(use_url=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше или равно 1'
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    image = Base64ImageField(use_url=True, required=True)
    author = UserSerializer()
    tags = TagSerializer(many=True, required=True)
    ingredients = RecipeIngredientGetSerializer(
        many=True, source='recipeingredients', required=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('id', 'author', 'tags', 'ingredients')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=user,
                                                 recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user,
                                               recipe=obj).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    image = Base64ImageField(use_url=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        write_only=True,
        required=True
    )

    def set_ingredients_and_tags(self, recipe, ingredients, tags):
        ingredients_ids = [ingredient.get('id') for ingredient in ingredients]
        ingredients_obj = Ingredient.objects.filter(id__in=ingredients_ids)
        ingredients_dict = {
            ingredient.id: ingredient for ingredient in ingredients_obj
        }
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredients_dict[ingredient['id']],
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)

    def validate_cooking_time(self, value):
        if value == 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return value

    def validate_image(self, value):
        if value is None:
            raise serializers.ValidationError('Поле image обязательно.')
        return value

    def validate_ingredients(self, ingredients):
        ingredients_list = [ingredient.get('id') for ingredient in ingredients]
        ingredients_amount = len(ingredients_list)
        if ingredients_amount == 0:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        elif not all(
            Ingredient.objects.filter(
                id=ingredient.get('id')
            ).exists() for ingredient in ingredients
        ):
            raise serializers.ValidationError(
                'Введенный ингредиент не существует'
            )
        elif ingredients_amount != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Поле tags обязательно.')
        elif len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги должны быть уникальными.')
        return tags

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.set_ingredients_and_tags(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is None or ingredients is None:
            raise serializers.ValidationError(
                'Отсутствуют теги или ингредиенты'
            )
        instance.ingredients.clear()
        instance.tags.clear()
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        self.set_ingredients_and_tags(instance, ingredients, tags)
        return instance

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author', 'tags', 'ingredients')

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецептов в избранном и списке покупок."""

    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowerSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
        read_only_fields = (
            'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follower.objects.filter(user=request.user,
                                       author=obj).exists()

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        query = obj.recipes.all()
        if limit:
            query = query[: int(limit)]
        recipes = ShoppingCartFavoriteSerializer(query, many=True)
        return recipes.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для короткой ссылки."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        model = ShortLink
        fields = ('short_link',)

    def get_short_link(self, obj):
        """Создает полный URL для короткой ссылки."""

        base_url = f'{settings.BASE_DIR}/s/'
        return f"{base_url}{obj.short_link}"

    def to_representation(self, instance):
        """Преобразует ключи в формат с дефисом."""

        representation = super().to_representation(instance)
        return {
            'short-link': representation['short_link']
        }
