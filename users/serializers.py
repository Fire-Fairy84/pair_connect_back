from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
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
            validated_data.pop('password2')
            password = validated_data.pop('password')
            user = CustomUser(**validated_data)
            user.set_password(password)
            user.save()
            return user
