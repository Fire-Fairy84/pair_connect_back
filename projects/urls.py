from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (ProjectViewSet, SessionViewSet, InterestedParticipantViewSet, get_suggested_developers,
                    get_developer_public_data, get_developer_private_data, get_suggested_sessions_for_user,
                    SessionsByProjectView, invite_developer_to_session, CheckUserInterestView, ConfirmParticipantView,
                    UserHostedSessionsView, UserParticipatingSessionsView, UserInterestedSessionsView, UserSessionsView)


router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"sessions", SessionViewSet)
router.register(r"interested-participants", InterestedParticipantViewSet)

urlpatterns = [
    path('project-sessions/<int:project_id>/', SessionsByProjectView.as_view(), name='sessions_by_project'),
    path('sessions/<int:session_id>/suggested-developers/', get_suggested_developers, name='suggested_developers'),
    path('users/suggested-sessions/', get_suggested_sessions_for_user, name='suggested_sessions'),
    path('projects/<int:project_id>/sessions/', SessionsByProjectView.as_view(), name='sessions_by_project'),
    path('sessions/<int:session_id>/developers/<int:developer_id>/invite/', invite_developer_to_session, name='invite_developer'),
    path('sessions/<int:session_id>/check-interest/', CheckUserInterestView.as_view(), name='check_interest'),
    path('sessions/<int:session_id>/confirm-participant/', ConfirmParticipantView.as_view(), name='confirm_participant'),
    path('users/sessions/hosted/', UserHostedSessionsView.as_view(), name='user_hosted_sessions'),
    path('users/sessions/participating/', UserParticipatingSessionsView.as_view(), name='user_participating_sessions'),
    path('users/sessions/interested/', UserInterestedSessionsView.as_view(), name='user_interested_sessions'),
    path('users/sessions/', UserSessionsView.as_view(), name='user_sessions'),
    path('', include(router.urls)),
]
