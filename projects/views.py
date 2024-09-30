from rest_framework import viewsets, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Session, InterestedParticipant
from .serializers import ProjectSerializer, SessionSerializer, InterestedParticipantSerializer
from .services import DeveloperSuggestionService
from users.serializers import CustomUserSerializer


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


@api_view(['GET'])
def get_suggested_developers(request, session_id):
    try:
        session = Session.objects.get(id=session_id)

        suggestion_service = DeveloperSuggestionService(session)
        suggested_developers = suggestion_service.get_suggested_developers()

        serializer = CustomUserSerializer(suggested_developers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Session.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
