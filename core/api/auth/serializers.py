from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        validated_data = super().validate(data)
        email = validated_data["email"]
        password = validated_data["password"]
        user = get_object_or_404(User, email=email)

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "In correct password"})

        return validated_data

    def save(self):
        email = self.validated_data["email"]
        return User.objects.get(email=email)


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                email=validated_data.pop("email"),
                password=validated_data.pop("password"),
            )
        except IntegrityError:
            raise serializers.ValidationError({"email": "Email Address already used"})
        user.username = user.email
        user.save()
        return user
