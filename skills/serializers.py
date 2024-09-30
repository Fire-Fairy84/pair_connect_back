from rest_framework import serializers
from .models import Stack, Level, ProgLanguage

class StackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stack
        fields = ['id', 'name']  # Adjust fields as necessary

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name']  # Adjust fields as necessary

class ProgLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgLanguage
        fields = ['id', 'name']