from api.pagination import LimitPagePagination
from api.permissions import IsAuthorAdminAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            ShortLink, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follower, User

from .filters import IngredientFilter, RecipeFilter
from .serializers import (AvatarUserSerializer, FollowerSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeGetSerializer, ShoppingCartFavoriteSerializer,
                          ShortLinkSerializer, TagSerializer, UserSerializer)
from .utils import create_shopping_list


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет получения тегов по id.
    Редактирование и добавление тегов доступно только через админку.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет получения ингредиентов по id.
    Редактирование и добавление ингредиентов доступно через админку.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов.
    Просматривать рецепты могут все пользователи.
    Создание рецептов доступно только аутентифицированным пользователям.
    Редактирование/удаление доступно только автору или админу.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminAuthenticated,)
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):

        if self.action == 'list' or self.action == 'retrieve':
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @staticmethod
    def create_or_delete_related_objects(request, model, serializer, pk):
        """Статический метод для удаления/добавления
        рецептов в список покупок и избранное.
        """

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if model.objects.filter(
                user=user,
                    recipe=recipe
            ).exists():
                return Response(
                    'Нельзя повторно добавить объект',
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            return Response(
                serializer(recipe).data, status=status.HTTP_201_CREATED
            )
        try:
            model.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                'Необходимо сначала добавить объект',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """Вью для добавления и удаления из списка покупок."""

        return self.create_or_delete_related_objects(
            request,
            ShoppingCart,
            ShoppingCartFavoriteSerializer,
            pk
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Вью для добавления и удаления рецептов из избранного."""

        return self.create_or_delete_related_objects(
            request,
            FavoriteRecipe,
            ShoppingCartFavoriteSerializer,
            pk
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Вью для скачивания списка покупок в формате txt."""

        file = create_shopping_list(request.user)
        response = HttpResponse(
            file,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')
        return response

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_link(self, request, pk=None):
        """Получить короткую ссылку на рецепт."""

        recipe = self.get_object()
        short_link, created = ShortLink.objects.get_or_create(recipe=recipe)
        serializer = ShortLinkSerializer(short_link)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет кастомной модели пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagePagination
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Подписаться/отписаться."""

        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'message': 'Вы хотите подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif Follower.objects.filter(author=author, user=user).exists():
                return Response(
                    'Вы пытаетесь подписаться повторно',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follower.objects.create(user=user, author=author)
            serializer = FollowerSerializer(
                author,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            author_del = Follower.objects.filter(user=user, author=author)
            if author_del.exists():
                author_del.delete()
                return Response(
                    {'message': 'Вы отписались от автора'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'message': 'Вы не подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowerSerializer,
    )
    def subscriptions(self, request, *args, **kwargs):
        """Получение списка всех подписок на пользователей."""

        user = request.user
        following = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(following)
        if pages is not None:
            serializer = FollowerSerializer(
                pages, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(pages, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=('put',), url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request, *args, **kwargs):
        """Вью для установки аватара пользователя."""

        user = request.user
        serializer = AvatarUserSerializer(user, data=request.data)
        if not request.data.get('avatar'):
            return Response(
                {"detail": "Аватар не был предоставлен."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        """Вью для удаления аватара пользователя."""

        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Аватар не установлен.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_short_link(request, recipe_id):
    """
    Получение или создание короткой ссылки для рецепта.
    """

    recipe = get_object_or_404(Recipe, id=recipe_id)

    short_link, created = ShortLink.objects.get_or_create(recipe=recipe)

    serializer = ShortLinkSerializer(short_link)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def redirect_short_link(request, short_link):
    """Перенаправляет на соответствующий рецепт по короткой ссылке."""

    short_link_obj = get_object_or_404(ShortLink, short_link=short_link)
    return redirect('recipes-detail', pk=short_link_obj.recipe.id)
