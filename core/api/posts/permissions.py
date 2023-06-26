from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated


class PostPermission(IsAuthenticated):
    def has_object_permission(self, request, view, object):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.pk == object.author.pk
        )

    def has_permission(self, request, view):
        safe_methods = request.method in permissions.SAFE_METHODS
        is_authenticated = super().has_permission(request, view)
        return safe_methods or (is_authenticated and hasattr(request.user, "author"))
