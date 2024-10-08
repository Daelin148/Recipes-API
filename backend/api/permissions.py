from rest_framework import permissions


class IsAuthorAdminAuthenticated(permissions.BasePermission):
    """
    Пермишн для проверки является ли пользователь автором рецепта либо админом.
    В остальных случаях доступ для чтения.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author
                or request.user.is_superuser)
