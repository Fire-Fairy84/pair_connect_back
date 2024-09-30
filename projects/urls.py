from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SessionViewSet, InterestedParticipantViewSet, get_suggested_developers

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'interested-participants', InterestedParticipantViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('sessions/<int:session_id>/suggested-developers/', get_suggested_developers, name='suggested_developers'),
]
