from rest_framework import serializers
from .models import Project, Session, InterestedParticipant


class ProjectSerializer(serializers.ModelSerializer):
    stack = serializers.StringRelatedField()
    class Meta:
        model = Project
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class InterestedParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestedParticipant
        fields = '__all__'
