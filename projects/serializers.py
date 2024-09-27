from rest_framework import serializers
from .models import Project, Session, InterestedParticipant


class ProjectSerializer(serializers.ModelSerializer):
    # stack = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = '__all__'


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
