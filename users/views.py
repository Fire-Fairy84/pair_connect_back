from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from projects.models import Session

from .services import UserProfileService

User = get_user_model()


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(
            {"detail": "User account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
                )
            except TokenError:
                return Response(
                    {
                        "detail": "Token expired or invalid, but logged out successfully."
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"detail": "Logged out, no token provided or token expired."},
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, session_id=None):
        try:
            session = None
            if session_id:
                session = Session.objects.get(id=session_id)

            profile_service = UserProfileService(request.user, user_id)
            profile_data = profile_service.get_profile_data(session)

            return Response(profile_data, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            return Response(
                {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
