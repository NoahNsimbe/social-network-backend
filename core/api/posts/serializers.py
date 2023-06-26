from rest_framework import serializers

from core.api.user.serializers import UserPublicSerializer, UserPrivateSerializer
from core.models import Post
from core.utils import generate_post_slug


class PostPrivateSerializer(serializers.ModelSerializer):
    likes = UserPublicSerializer(read_only=True, many=True)
    author = UserPrivateSerializer(required=False)

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "author",
            "deleted_at",
            "is_deleted",
            "likes",
        )
        extra_kwargs = {
            "message": {"required": True},
        }

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        user = self.context["request"].user
        validated_data["author"] = user
        return validated_data

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        generate_post_slug(post)
        return post


class LikePostPublicSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=True)

    def validate(self, data):
        user = self.context["request"].user
        validated_data = super().validate(data)
        validated_data["user"] = user
        return validated_data

    def save(self):
        post: Post = self.validated_data["id"]
        likes = set(post.likes.all())
        likes.add(self.validated_data["user"])
        post.likes.set(likes)
        return post


class UnlikePostPublicSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=True)

    def validate(self, data):
        user = self.context["request"].user
        validated_data = super().validate(data)
        validated_data["user"] = user
        return validated_data

    def save(self):
        post: Post = self.validated_data["id"]
        likes = set(post.likes.all())
        likes.remove(self.validated_data["user"])
        post.likes.set(likes)
        return post


class PostPublicSerializer(serializers.ModelSerializer):
    likes = UserPublicSerializer(read_only=True, many=True)
    author = UserPublicSerializer()

    class Meta:
        model = Post
        fields = (
            "author",
            "id",
            "created_at",
            "updated_at",
            "likes",
            "message",
        )
