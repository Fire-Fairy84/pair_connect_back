from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser
from .services import create_user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'name',
            'password',
            'password2',
            'photo',
            'about_me',
            'telephone',
            'linkedin_link',
            'github_link',
            'discord_link',
            'stack',
            'level',
            'prog_language',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        try:
            user = create_user(**validated_data)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'name',
            'photo',
            'about_me',
            'telephone',
            'linkedin_link',
            'github_link',
            'discord_link',
            'stack',
            'level',
            'prog_language',
        ]
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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        return attrs


class LogoutSerializer(serializers.Serializer):
    pass
