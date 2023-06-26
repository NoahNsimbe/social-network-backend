from rest_framework.permissions import IsAuthenticated


class UserPermission(IsAuthenticated):
    def has_object_permission(self, request, view, object):
        is_valid = super().has_object_permission(request, view, object)
        is_owner = request.user.pk == object.pk
        return is_valid and is_owner
