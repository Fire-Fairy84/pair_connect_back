from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SessionViewSet, InterestedParticipantViewSet, ProjectCreateView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'interested-participants', InterestedParticipantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
