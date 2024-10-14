from rest_framework import serializers
from .models import Stack, Level, ProgLanguage


class StackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stack
        fields = ['id', 'name']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name']


class ProgLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgLanguage
        fields = ['id', 'name']
