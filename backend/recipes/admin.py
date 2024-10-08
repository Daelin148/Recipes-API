from django.contrib import admin
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, ShortLink, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    search_fields = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = search_fields = ('user', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = search_fields = ('user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_editable = ('name', 'measurement_unit')


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.validate_min = True
        return formset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = search_fields = ('id', 'name', 'author', 'favorites_count')
    list_filter = ('tags', 'author')
    readonly_fields = ('author', 'favorites_count')
    inlines = (IngredientsInline,)

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

    @admin.display(description='Количество избранных рецептов')
    def favorites_count(self, obj):
        return obj.favorite.count()


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'short_link')
    list_editable = ('recipe', 'short_link')
