from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserViewSet, get_short_link)
from django.urls import include, path
from rest_framework import routers

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients',
                   IngredientViewSet,
                   basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:recipe_id>/get-link/', get_short_link, name='get-link'),
    path('', include(router_v1.urls)),
]
