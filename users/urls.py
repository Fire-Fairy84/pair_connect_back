from django.urls import path, include
from .views import LogoutView
from rest_framework import routers
from .views import DeleteAccountView

router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)
#
urlpatterns = [
    path('jwt/logout/', LogoutView.as_view(), name='jwt-logout'),
    path('users/delete/', DeleteAccountView.as_view(), name='delete-account'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/delete/', DeleteAccountView.as_view(), name='delete_account'),
    path('', include(router.urls)),
]
