from rest_framework import serializers

from skills.models import Level, ProgLanguage, Stack
from users.models import CustomUser
from users.serializers import CustomUserSerializer

from .models import InterestedParticipant, Project, Session


class SessionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    owner_id = serializers.PrimaryKeyRelatedField(source="host", read_only=True)
    owner_name = serializers.CharField(source="host.username", read_only=True)
    owner_avatar_url = serializers.ReadOnlyField(source="host.photo.url")
    stack_id = serializers.PrimaryKeyRelatedField(
        source="stack", queryset=Stack.objects.all(), write_only=True
    )
    stack_name = serializers.CharField(source="stack.name", read_only=True)
    level_id = serializers.PrimaryKeyRelatedField(
        source="level",
        queryset=Level.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    level_name = serializers.CharField(source="level.name", read_only=True)
    language_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source="languages",
        queryset=ProgLanguage.objects.all(),
        write_only=True,
    )
    language_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name", source="languages"
    )
    project_id = serializers.IntegerField(source="project.id", read_only=True)
    description = serializers.CharField(required=False, allow_blank=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_image_url = serializers.SerializerMethodField()
    participants = CustomUserSerializer(many=True, read_only=True)
    session_link = serializers.URLField(required=False, allow_blank=True)
    participant_limit = serializers.IntegerField(required=False, allow_null=True)
    is_private = serializers.BooleanField(write_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "name",
            "description",
            "schedule_date_time",
            "duration",
            "stack_id",
            "stack_name",
            "level_id",
            "level_name",
            "language_ids",
            "language_names",
            "project_id",
            "project_name",
            "project_image_url",
            "owner_id",
            "owner_name",
            "owner_avatar_url",
            "participants",
            "session_link",
            "participant_limit",
            "is_private",
            "public",
        ]

    def validate_languages(self, value):
        project_id = self.initial_data.get("project")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(
                f"Project with id {project_id} does not exist."
            )

        project_languages_ids = set(project.languages.values_list("id", flat=True))
        for language in value:
            if language.id not in project_languages_ids:
                raise serializers.ValidationError(
                    f"Language {language.name} is not part of the project."
                )

        return value

    def update(self, instance, validated_data):
        instance.session_link = validated_data.get("session_link", instance.session_link)
        instance.participant_limit = validated_data.get("participant_limit", instance.participant_limit)
        instance.description = validated_data.get("description", instance.description)
        instance.schedule_date_time = validated_data.get("schedule_date_time", instance.schedule_date_time)
        instance.duration = validated_data.get("duration", instance.duration)
        is_private = validated_data.get("is_private", None)
        if is_private is not None:
            instance.public = not is_private
        participant_limit = validated_data.get('participant_limit', instance.participant_limit)
        if participant_limit is None:
            validated_data['participant_limit'] = 0

        instance.save()
        print("Updated Instance:", instance)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["is_private"] = not instance.public
        return representation

    def get_project_image_url(self, obj):
        if obj.project and obj.project.image:
            base_url = "https://res.cloudinary.com/dwzqcmaod/image/upload/"
            return f"{base_url}{obj.project.image}"
        return None


class SessionDetailSerializer(SessionSerializer):
    session_link = serializers.URLField(read_only=True)
    active = serializers.BooleanField(read_only=True)
    public = serializers.BooleanField(read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta(SessionSerializer.Meta):
        fields = SessionSerializer.Meta.fields + [
            "session_link",
            "active",
            "public",
            "participant_count",
            "project_name",
        ]

    def get_participant_count(self, obj):
        return obj.participants.count()


class SessionParticipantSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(), slug_field="username", many=True
    )

    class Meta:
        model = Session
        fields = ["participants"]


class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(source="owner", read_only=True)
    owner_avatar_url = serializers.SerializerMethodField()
    image_url = serializers.CharField(source="image.url", read_only=True)
    stack = serializers.PrimaryKeyRelatedField(
        queryset=Stack.objects.all(), write_only=True
    )
    stack_name = serializers.CharField(source="stack.name", read_only=True)
    languages = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ProgLanguage.objects.all(), write_only=True
    )
    language_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name", source="languages"
    )
    level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(), write_only=True
    )
    level_name = serializers.CharField(source="level.name", read_only=True)
    sessions = SessionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "image",
            "stack",
            "stack_name",
            "languages",
            "language_names",
            "level",
            "level_name",
            "image_url",
            "owner_id",
            "owner_name",
            "owner_avatar_url",
            "sessions",
        ]

    def create(self, validated_data):
        languages_data = validated_data.pop("languages")
        project = Project.objects.create(
            owner=self.context["request"].user, **validated_data
        )
        project.languages.set(languages_data)
        return project

    def update(self, instance, validated_data):
        languages_data = validated_data.pop("languages", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if languages_data is not None:
            instance.languages.set(languages_data)
        instance.save()
        return instance

    def validate_stack(self, value):
        if not Stack.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected stack does not exist.")
        return value

    def validate_level(self, value):
        if not Level.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected level does not exist.")
        return value

    def validate_languages(self, value):
        if not value:
            raise serializers.ValidationError("At least one language must be selected.")
        return value

    def get_owner_avatar_url(self, obj):
        if obj.owner and obj.owner.photo:
            base_url = "https://res.cloudinary.com/dwzqcmaod/image/upload/"
            return f"{base_url}{obj.owner.photo}"
        return None


class InterestedParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestedParticipant
        fields = ["session", "date_created_interested"]
