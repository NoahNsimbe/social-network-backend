from rest_framework import serializers

from core.models import User, UserMetaData


class UserMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMetaData
        fields = (
            "geo_data",
            "public_holidays",
        )


class UserPrivateSerializer(serializers.ModelSerializer):
    meta_data = UserMetaDataSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "email_verified",
            "meta_data",
        )


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
        )
