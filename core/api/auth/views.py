from rest_framework import viewsets, response, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from core.utils import get_refresh_and_access_tokens
from .serializers import (
    LoginSerializer,
    SignupSerializer,
)
from ..user.serializers import UserPrivateSerializer
from ...tasks import save_user_meta_data


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    @action(methods=["POST"], detail=False, serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh_token, access_token = get_refresh_and_access_tokens(user=user)
        return response.Response(
            UserPrivateSerializer(user).data,
            headers={
                "set-auth-token": access_token,
                "set-auth-refresh-token": refresh_token,
            },
        )

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=SignupSerializer,
    )
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh_token, access_token = get_refresh_and_access_tokens(user=user)

        ip_address = request.META.get("REMOTE_ADDR", "")
        save_user_meta_data.delay(ip_address, user.email)

        return response.Response(
            UserPrivateSerializer(user).data,
            status=status.HTTP_201_CREATED,
            headers={
                "set-auth-token": access_token,
                "set-auth-refresh-token": refresh_token,
            },
        )
