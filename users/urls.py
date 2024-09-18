from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, UserCreateView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserCreateView.as_view(), name='user-register'),
]
