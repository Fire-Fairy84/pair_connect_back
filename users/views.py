from rest_framework import viewsets, generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import UserRegistrationSerializer, LoginSerializer, LogoutSerializer, UserProfileSerializer
from .services import authenticate_user
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_data = authenticate_user(**serializer.validated_data)
                user_serializer = UserProfileSerializer(user_data['user'], context={'request': request})
                return Response({
                    'token': user_data['token'],
                    'user': user_serializer.data,
                }, status=status.HTTP_200_OK)
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except AttributeError:
            return Response({"detail": "Token does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response({"detail": "Token already deleted."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
