from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    only allow access to superusers.
    """
    def has_permission(self, request, view):
        # check if the user is authenticated and is a superuser
        return request.user and request.user.is_authenticated and request.user.is_superuser