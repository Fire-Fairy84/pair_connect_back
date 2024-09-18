from rest_framework import viewsets, generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)


class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
