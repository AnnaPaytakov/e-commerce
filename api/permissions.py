from rest_framework import permissions

#only allow access to superusers.
class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # check if the user is authenticated and is a superuser
        return request.user and request.user.is_authenticated and request.user.is_superuser