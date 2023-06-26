from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import PostFilter
from .permissions import PostPermission
from .serializers import (
    PostPublicSerializer,
    PostPrivateSerializer,
    LikePostPublicSerializer,
    UnlikePostPublicSerializer,
)
from ...models import Post


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [PostPermission]
    filterset_class = PostFilter
    serializer_class = PostPublicSerializer
    queryset = Post.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return PostPrivateSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        post.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False)
    def like(self, request):
        query_params = self.request.query_params

        serializer = LikePostPublicSerializer(
            data=query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return response.Response(PostPublicSerializer(post).data)

    @action(methods=["GET"], detail=False)
    def unlike(self, request):
        query_params = self.request.query_params

        serializer = UnlikePostPublicSerializer(
            data=query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return response.Response(PostPublicSerializer(post).data)
