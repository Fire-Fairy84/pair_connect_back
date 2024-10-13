from django.urls import include, path
from rest_framework import routers
from .views import DeleteAccountView, LogoutView, UserProfileView

router = routers.DefaultRouter()


urlpatterns = [
    path("users/delete/", DeleteAccountView.as_view(), name="delete-account"),
    path(
        "users/<int:user_id>/profile/", UserProfileView.as_view(), name="user_profile"
    ),
    path(
        "users/<int:user_id>/profile/<int:session_id>/",
        UserProfileView.as_view(),
        name="user_profile_with_session",
    ),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/delete/", DeleteAccountView.as_view(), name="delete_account"),
    path("", include(router.urls)),
]
