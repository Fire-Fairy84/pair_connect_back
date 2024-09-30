from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SessionViewSet, InterestedParticipantViewSet, get_suggested_developers, get_developer_public_data, get_developer_private_data

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'interested-participants', InterestedParticipantViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('sessions/<int:session_id>/suggested-developers/', get_suggested_developers, name='suggested_developers'),
    path('sessions/<int:session_id>/developers/<int:developer_id>/public/', get_developer_public_data, name='developer_public_data'),
    path('sessions/<int:session_id>/developers/<int:developer_id>/private/', get_developer_private_data, name='developer_private_data'),
]
