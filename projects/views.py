from rest_framework import viewsets, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Project, Session, InterestedParticipant
from .serializers import ProjectSerializer, SessionSerializer, InterestedParticipantSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class InterestedParticipantViewSet(viewsets.ModelViewSet):
    queryset = InterestedParticipant.objects.all()
    serializer_class = InterestedParticipantSerializer
