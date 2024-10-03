from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from skills.models import Stack, Level, ProgLanguage
from .models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'name', 'password', 're_password', 'photo',
            'about_me', 'telephone', 'linkedin_link', 'github_link', 'discord_link',
            'stack', 'level', 'prog_language'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            're_password': {'write_only': True},
        }

    def create(self, validated_data):
        stack = validated_data.pop('stack', None)
        level = validated_data.pop('level', None)
        prog_language = validated_data.pop('prog_language', None)

        user = super().create(validated_data)

        # Assign ForeignKey fields
        if stack:
            user.stack = Stack.objects.get(id=stack)
        if level:
            user.level = Level.objects.get(id=level)
        if prog_language:
            user.prog_language = ProgLanguage.objects.get(id=prog_language)

        user.save()

        return user


class CustomUserSerializer(UserSerializer):
    photo_url = serializers.CharField(source='image.url', read_only=True)
    stack = serializers.PrimaryKeyRelatedField(queryset=Stack.objects.all(), allow_null=True)
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all(), allow_null=True)
    prog_language = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProgLanguage.objects.all()
    )
    stack_name = serializers.CharField(source='stack.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    language_names = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name', source='prog_language')

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'name', 'photo', 'about_me',
            'telephone', 'linkedin_link', 'github_link', 'discord_link',
            'stack', 'level', 'prog_language', 'photo_url',
        )
        read_only_fields = ['id', 'username', 'email']

    def validate(self, data):
        request = self.context.get('request', None)
        if request and request.method in ['PUT', 'PATCH']:
            if 'username' in request.data:
                raise serializers.ValidationError({'username': 'Username cannot be changed.'})
            if 'email' in request.data:
                raise serializers.ValidationError({'email': 'Email cannot be changed.'})
        return data

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

    def update(self, instance, validated_data):
        prog_languages = validated_data.pop('prog_language', None)

        instance = super().update(instance, validated_data)

        if prog_languages:
            instance.prog_language.set(prog_languages)

        return instance

    def to_representation(self, instance):
        """Override to adjust photo URL format."""
        representation = super().to_representation(instance)
        if instance.photo:
            base_url = 'https://res.cloudinary.com/dwzqcmaod/image/upload/'
            photo_url = str(instance.photo)
            if not photo_url.startswith('http'):
                representation['photo'] = f"{base_url}{photo_url}"
            else:
                representation['photo'] = photo_url
        return representation


class PublicDeveloperSerializer(serializers.ModelSerializer):
    stack_name = serializers.CharField(source='stack.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    language_names = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name', source='prog_language')
    class Meta:
        model = CustomUser
        fields = (
            'name', 'username', 'photo', 'stack', 'prog_language', 'level', 'about_me', 'stack_name', 'level_name', 'language_names'
        )

    def to_representation(self, instance):
        """Override to adjust photo URL format."""
        representation = super().to_representation(instance)
        if instance.photo:
            base_url = 'https://res.cloudinary.com/dwzqcmaod/image/upload/'
            photo_url = str(instance.photo)
            if not photo_url.startswith('http'):
                representation['photo'] = f"{base_url}{photo_url}"
            else:
                representation['photo'] = photo_url
        return representation


class PrivateDeveloperSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'name', 'username', 'photo', 'stack', 'prog_language', 'level', 'about_me',
            'email', 'telephone', 'linkedin_link', 'github_link', 'discord_link', 'stack_name', 'level_name', 'language_names',
        )

        def to_representation(self, instance):
            """Override to adjust photo URL format."""
            representation = super().to_representation(instance)
            if instance.photo:
                base_url = 'https://res.cloudinary.com/dwzqcmaod/image/upload/'
                photo_url = str(instance.photo)
                if not photo_url.startswith('http'):
                    representation['photo'] = f"{base_url}{photo_url}"
                else:
                    representation['photo'] = photo_url
            return representation
