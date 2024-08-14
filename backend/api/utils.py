from django.db.models import Sum
from recipes.models import RecipeIngredient


def create_shopping_list(user):
    """Функция формирует список ингредиентов в корзине."""

    shopping_cart = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
        amount=Sum('amount')
    )
    shopping_list = ['Ваш список покупок:\n']
    ingredient_list = (
        (f'{ingredient["ingredient__name"]}: '
         f'{ingredient["amount"]} '
         f'{ingredient["ingredient__measurement_unit"]}')
        for ingredient in shopping_cart
    )
    shopping_list.extend(ingredient_list)

    return '\n'.join(shopping_list)
