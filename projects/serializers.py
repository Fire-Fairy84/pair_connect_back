from rest_framework import serializers
from skills.models import Stack, Level, ProgLanguage
from .models import Project, Session, InterestedParticipant


class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    # Return the `stack.name`, `level.name`, and `languages.name` for display while accepting their IDs for creation.
    stack = serializers.PrimaryKeyRelatedField(queryset=Stack.objects.all(),write_only=True)  # For writing (when creating/updating)
    stack_name = serializers.CharField(source='stack.name', read_only=True)  # For reading (displaying stack name)
    languages = serializers.PrimaryKeyRelatedField(many=True, queryset=ProgLanguage.objects.all(), write_only=True)  # For writing (when creating/updating)
    language_names = serializers.SlugRelatedField( many=True, read_only=True, slug_field='name', source='languages')  # For reading (displaying language names)
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all(),write_only=True)  # For writing (when creating/updating)
    level_name = serializers.CharField(source='level.name', read_only=True)  # For reading (displaying level name)


    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'image', 'stack', 'stack_name', 'languages', 'language_names', 'level', 'level_name', 'image_url']
        # Exclude 'owner' and 'active' from user input

    def create(self, validated_data):
        image = validated_data.get('image')
        print(f"Image received in create method: {image}")  # Check if the image is received
        # Extract languages
        languages_data = validated_data.pop('languages')
        # Create project without 'owner'
        project = Project.objects.create(owner=self.context['request'].user, **validated_data)
        # Set languages
        project.languages.set(languages_data)
        return project

    def get_image_url(self, obj):
        return obj.image_url()

    def update(self, instance, validated_data):
        languages_data = validated_data.pop('languages', None)
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


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

    def validate_languages(self, value):
        project_id = self.initial_data.get('project')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(f"Project with id {project_id} does not exist.")

        project_languages_ids = set(project.languages.values_list('id', flat=True))

        for language in value:
            if language.id not in project_languages_ids:
                raise serializers.ValidationError(f"Language {language.name} is not part of the project.")

        return value


class InterestedParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestedParticipant
        fields = '__all__'
