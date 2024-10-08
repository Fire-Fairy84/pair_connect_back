from rest_framework import viewsets, generics, permissions, status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from users.services import DeveloperDataService
from .models import Project, Session, InterestedParticipant, Session
from .serializers import ProjectSerializer, SessionSerializer, InterestedParticipantSerializer, SessionParticipantSerializer
from .services import DeveloperSuggestionService, InvitationService, SessionSuggestionService, SessionCreationService
from users.serializers import CustomUserSerializer
from users.models import CustomUser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        if not project_id:
            raise serializers.ValidationError("Project ID is required to create a session.")

        if not Project.objects.filter(id=project_id).exists():
            raise serializers.ValidationError("Project does not exist.")

        session_data = serializer.validated_data

        session = SessionCreationService.handle_create_session(self.request.user, project_id, session_data)
        serializer.instance = session


class SessionsByProjectView(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Session.objects.filter(project__id=project_id)



class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionParticipantSerializer
    permission_classes = [IsAuthenticated]  

    @action(detail=True, methods=['post'], url_path='confirm-participant')
    def confirm_participant(self, request, pk=None):
        session = get_object_or_404(Session, pk=pk)

        if session.host != request.user:
            return Response({"error": "Only the host can confirm participants."}, status=status.HTTP_403_FORBIDDEN)

        developer_username = request.data.get('username')
        developer = get_object_or_404(CustomUser, username=developer_username)

        if session.participants.count() >= session.participant_limit > 0:
            return Response({"error": "Participant limit reached."}, status=status.HTTP_400_BAD_REQUEST)

        session.participants.add(developer)

        return Response({"message": f"Developer {developer.username} has been confirmed for the session."}, status=status.HTTP_200_OK)


class InterestedParticipantViewSet(viewsets.ModelViewSet):
    queryset = InterestedParticipant.objects.all()
    serializer_class = InterestedParticipantSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        """
            Create a new interested participant
        """
        try:
            session_id = self.request.data.get('session')
            if not session_id:
                raise ValidationError("Session ID is required.")

            session = get_object_or_404(Session, id=session_id)

            if InterestedParticipant.objects.filter(user=self.request.user, session=session).exists():
                raise ValidationError("You are already interested in this session.")

            interested_participant = serializer.save(user=self.request.user)

            return Response(
                {
                    "message": "You have successfully expressed interest in this session.",
                    "participant": InterestedParticipantSerializer(interested_participant).data
                }, 
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_409_CONFLICT
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=True, methods=['get'], url_path='interested-users')
    def get_interested_users(self, request, pk=None):
        """
            Get all interested users for a session
        """
        session = get_object_or_404(Session, id=pk)
        interested_participants = InterestedParticipant.objects.filter(session=session).select_related('user')

        users = [participant.user for participant in interested_participants]
        serializer = CustomUserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckUserInterestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = get_object_or_404(Session, id=session_id)

            is_interested = InterestedParticipant.objects.filter(user=request.user, session=session).exists()

            return Response({"is_interested": is_interested}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        EmailService.send_invite_email(session, developer)

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