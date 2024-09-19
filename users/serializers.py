from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser
from .services import create_user


class UserSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        try:
            user = create_user(**validated_data)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        return user
