from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
            except TokenError:
                return Response({"detail": "Token expired or invalid, but logged out successfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "Logged out, no token provided or token expired."}, status=status.HTTP_200_OK)
