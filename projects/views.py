from rest_framework import viewsets
from .models import Project, Session, InterestedParticipant
from .serializers import ProjectSerializer, SessionSerializer, InterestedParticipantSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class InterestedParticipantViewSet(viewsets.ModelViewSet):
    queryset = InterestedParticipant.objects.all()
    serializer_class = InterestedParticipantSerializer
