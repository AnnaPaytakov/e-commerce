from rest_framework import permissions

#* allow access only to superusers
class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_superuser
        )