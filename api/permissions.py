from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только суперюзерам (is_superuser=True).
    """
    def has_permission(self, request, view):
        # Проверяем, аутентифицирован ли пользователь и является ли он суперюзером
        return request.user and request.user.is_authenticated and request.user.is_superuser