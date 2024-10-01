from rest_framework import viewsets, generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.services import DeveloperDataService
from .models import Project, Session, InterestedParticipant, Session
from .serializers import ProjectSerializer, SessionSerializer, InterestedParticipantSerializer
from .services import DeveloperSuggestionService, InvitationService, SessionSuggestionService
from users.serializers import CustomUserSerializer
from users.models import CustomUser


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def invite_developer_to_session(request, session_id, developer_id):
    try:
        session = Session.objects.get(id=session_id)
        developer = CustomUser.objects.get(id=developer_id)
        invitation_service = InvitationService(session, developer)
        invitation_service.send_invitation()

        return Response({"message": "Invitation sent successfully"}, status=status.HTTP_200_OK)

    except Session.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response({"error": "Developer not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_developer_public_data(request, session_id, developer_id):
    try:
        developer_data_service = DeveloperDataService(session_id, developer_id)
        developer_data = developer_data_service.get_developer_data()

        return Response(developer_data, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_developer_private_data(request, session_id, developer_id):
    try:
        developer_data_service = DeveloperDataService(session_id, developer_id)
        developer_data = developer_data_service.get_developer_data(public=False)

        return Response(developer_data, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_suggested_sessions_for_user(request):
    try:
        user = request.user

        session_suggestion_service = SessionSuggestionService(user)
        suggested_sessions = session_suggestion_service.get_suggested_sessions()

        serializer = SessionSerializer(suggested_sessions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
