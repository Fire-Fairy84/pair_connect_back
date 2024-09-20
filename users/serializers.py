from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'name', 'password', 're_password', 'photo', 'about_me', 'telephone', 'linkedin_link',
            'github_link',
            'discord_link', 'stack', 'level', 'prog_language')
        extra_kwargs = {
            'password': {'write_only': True},
            're_password': {'write_only': True},
        }


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'name', 'photo', 'about_me', 'telephone', 'linkedin_link', 'github_link',
                  'discord_link', 'stack', 'level', 'prog_language')
        read_only_fields = ['id']

    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
