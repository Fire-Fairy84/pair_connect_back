from rest_framework import serializers
from skills.models import Stack, Level
from .models import Project, Session, InterestedParticipant


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'image', 'stack', 'languages', 'level']
        # Exclude 'owner' and 'active' from user input

    def create(self, validated_data):
        # Extract languages
        languages_data = validated_data.pop('languages')
        # Create project without 'owner'
        project = Project.objects.create(owner=self.context['request'].user, **validated_data)
        # Set languages
        project.languages.set(languages_data)
        return project

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
