from rest_framework import viewsets
from .models import Stack, Level, ProgLanguage
from .serializers import StackSerializer, LevelSerializer, ProgLanguageSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class StackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stack.objects.all()
    serializer_class = StackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProgLanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgLanguage.objects.all()
    serializer_class = ProgLanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]