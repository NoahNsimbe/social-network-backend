from rest_framework import viewsets, mixins, response, status
from rest_framework.decorators import action

from core.models import User
from .permissions import UserPermission
from .serializers import UserPrivateSerializer


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [UserPermission]
    serializer_class = UserPrivateSerializer
    queryset = User.objects.filter(is_deleted=False)

    @action(methods=["GET"], detail=False, permission_classes=[UserPermission])
    def me(self, request):
        user = request.user
        return response.Response(
            UserPrivateSerializer(user).data, status=status.HTTP_200_OK
        )
