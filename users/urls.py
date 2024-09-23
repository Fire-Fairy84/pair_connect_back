from django.urls import path, include
from .views import LogoutView
from rest_framework import routers

router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)
#
urlpatterns = [
    path('jwt/logout/', LogoutView.as_view(), name='jwt-logout'),
    path('', include(router.urls)),
]
